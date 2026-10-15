"""Mesh every device in the guide with Gmsh and write meshes/<id>.json.

The geometry is built with the OpenCASCADE kernel. The output holds:
  parts  - the surface triangles of each part (the 3D model that the page shows)
  air    - the triangles on the outside of the air box
  fem    - the conformal tetrahedral mesh: counts, plus a "crinkle cut" (the tetrahedra
           that cross a plane) to show the volume elements
  mom    - the surface triangles on the metal (top sheets only for planar 2.5D devices),
           with the number of RWG unknowns (inner edges)
  q2d    - a 2D cross-section mesh (stripline only)
Run with a Python that has gmsh and numpy, for example:
  python scripts/meshgen.py            (all devices)
  python scripts/meshgen.py aip cav    (some devices)
"""
import json, math, os, sys
import numpy as np
import gmsh

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "meshes")
METAL = {"gold", "copper", "steel", "alu", "solder"}


# ---------------------------------------------------------------- geometry helpers
def rot_vec(v, rot):
    """Rotate vector v by three.js Euler angles (order XYZ: R = Rx * Ry * Rz)."""
    rx, ry, rz = rot
    x, y, z = v
    x, y = x * math.cos(rz) - y * math.sin(rz), x * math.sin(rz) + y * math.cos(rz)
    x, z = x * math.cos(ry) + z * math.sin(ry), -x * math.sin(ry) + z * math.cos(ry)
    y, z = y * math.cos(rx) - z * math.sin(rx), y * math.sin(rx) + z * math.cos(rx)
    return (x, y, z)


class G:
    def __init__(self):
        self.occ = gmsh.model.occ
        self.parts = []  # (list of volume dimtags, material, gnd)

    def add(self, vols, mat, gnd=False):
        self.parts.append((vols, mat, gnd))

    def box(self, w, h, d, x, y, z, mat, rot=(0, 0, 0), gnd=False):
        t = self.occ.addBox(x - w / 2, y - h / 2, z - d / 2, w, h, d)
        if any(rot):
            for ax, ang in zip(((1, 0, 0), (0, 1, 0), (0, 0, 1)), rot):
                pass
            self._rotate([(3, t)], (x, y, z), rot)
        self.add([(3, t)], mat, gnd)
        return t

    def _rotate(self, dt, c, rot):
        # three.js XYZ order applies Rz first, then Ry, then Rx
        rx, ry, rz = rot
        if rz: self.occ.rotate(dt, *c, 0, 0, 1, rz)
        if ry: self.occ.rotate(dt, *c, 0, 1, 0, ry)
        if rx: self.occ.rotate(dt, *c, 1, 0, 0, rx)

    def cyl(self, r_top, r_bot, h, x, y, z, mat, rot=(0, 0, 0)):
        d = rot_vec((0, 1, 0), rot)
        bx, by, bz = x - d[0] * h / 2, y - d[1] * h / 2, z - d[2] * h / 2
        if abs(r_top - r_bot) < 1e-9:
            t = self.occ.addCylinder(bx, by, bz, d[0] * h, d[1] * h, d[2] * h, r_top)
        else:
            t = self.occ.addCone(bx, by, bz, d[0] * h, d[1] * h, d[2] * h, r_bot, r_top)
        self.add([(3, t)], mat)
        return t

    def sphere(self, r, x, y, z, mat, scale=None):
        t = self.occ.addSphere(x, y, z, r)
        if scale:
            self.occ.dilate([(3, t)], x, y, z, *scale)
        self.add([(3, t)], mat)

    def trace(self, pts, w, t, y, mat):
        vols = []
        for (x1, z1), (x2, z2) in zip(pts[:-1], pts[1:]):
            L = math.hypot(x2 - x1, z2 - z1)
            cx, cz = (x1 + x2) / 2, (z1 + z2) / 2
            b = self.occ.addBox(cx - (L + w) / 2, y - t / 2, cz - w / 2, L + w, t, w)
            ang = -math.atan2(z2 - z1, x2 - x1)
            if ang:
                self.occ.rotate([(3, b)], cx, y, cz, 0, 1, 0, ang)
            vols.append((3, b))
        self.add(vols, mat)

    def tube(self, pts, r, mat):
        ps = [self.occ.addPoint(*p) for p in pts]
        sp = self.occ.addBSpline(ps) if len(ps) > 2 else self.occ.addLine(*ps)
        wire = self.occ.addWire([sp])
        p0, p1 = np.array(pts[0]), np.array(pts[1])
        tan = (p1 - p0) / np.linalg.norm(p1 - p0)
        disk = self.occ.addDisk(*pts[0], r, r, zAxis=list(tan))
        vols = self.occ.addPipe([(2, disk)], wire)
        self.add([v for v in vols if v[0] == 3], mat)

    def prism(self, poly, plane, depth, offset, mat):
        """Extrude a polygon. plane 'xz' extrudes along y; 'xy' extrudes along z."""
        pts = []
        for a, b in poly:
            if plane == "xz":
                pts.append(self.occ.addPoint(offset[0] + a, offset[1], offset[2] + b))
            else:
                pts.append(self.occ.addPoint(offset[0] + a, offset[1] + b, offset[2]))
        lines = [self.occ.addLine(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
        s = self.occ.addPlaneSurface([self.occ.addCurveLoop(lines)])
        ext = self.occ.extrude([(2, s)], 0, depth if plane == "xz" else 0, 0 if plane == "xz" else depth)
        self.add([e for e in ext if e[0] == 3], mat)


# ---------------------------------------------------------------- devices (same geometry as the page builders)
def dev_aip(g):
    # 28 GHz antenna in package: 2x2 patch array on a 3-layer package, ground in the middle, feed vias, BGA balls, PCB below
    g.box(4.0, 0.12, 4.0, 0, 0.36, 0, "sub")            # top dielectric (antenna layer)
    g.box(4.0, 0.03, 4.0, 0, 0.285, 0, "copper", gnd=True)  # antenna ground
    g.box(4.0, 0.24, 4.0, 0, 0.15, 0, "sub")            # lower build-up layers
    g.box(4.0, 0.03, 4.0, 0, 0.015, 0, "copper", gnd=True)
    for x in (-0.9, 0.9):
        for z in (-0.9, 0.9):
            g.box(1.25, 0.03, 1.25, x, 0.435, z, "copper")      # patch
            g.cyl(0.06, 0.06, 0.42, x - 0.3, 0.21, z, "copper")  # feed via
    g.box(1.4, 0.18, 1.4, 0, -0.09, 0, "gaas")          # RFIC die under the package
    for i in range(-3, 4):
        for k in range(-3, 4):
            if abs(i) <= 1 and abs(k) <= 1:
                continue
            g.sphere(0.14, i * 0.55, -0.12, k * 0.55, "solder")
    g.box(5.0, 0.3, 5.0, 0, -0.41, 0, "sub")            # PCB
    return dict(radiate=True)


def dev_spiral(g):
    g.box(3.2, 0.5, 3.2, 0, -0.25, 0, "gaas")
    pts = [(-1.5, 0.9), (-0.9, 0.9), (-0.9, -0.9), (0.9, -0.9), (0.9, 0.9), (-0.6, 0.9), (-0.6, -0.6), (0.6, -0.6), (0.6, 0.6), (-0.3, 0.6), (-0.3, -0.3), (0.3, -0.3), (0.3, 0.3)]
    g.trace(pts, 0.16, 0.06, 0.03, "gold")
    g.trace([(0.3, 0.3), (0.3, 1.5)], 0.14, 0.05, 0.16, "gold")
    g.cyl(0.06, 0.06, 0.13, 0.3, 0.1, 0.3, "gold")
    return {}


def dev_mmic(g):
    g.box(4, 0.3, 2.6, 0, -0.15, 0, "gaas"); g.box(4, 0.04, 2.6, 0, -0.32, 0, "gold", gnd=True)
    g.trace([(-2, 0), (-1.2, 0), (-1.2, 0.6), (-0.4, 0.6)], 0.14, 0.04, 0.02, "gold")
    g.box(0.5, 0.06, 0.5, -0.1, 0.03, 0.6, "gold")
    g.trace([(0.15, 0.6), (0.6, 0.6), (0.6, -0.5), (1.3, -0.5), (1.3, 0), (2, 0)], 0.14, 0.04, 0.02, "gold")
    g.trace([(0.9, 0.5), (1.6, 0.5), (1.6, 1.0), (1.0, 1.0), (1.0, 0.65), (1.4, 0.65)], 0.08, 0.04, 0.02, "gold")
    g.box(0.6, 0.08, 0.5, -0.9, 0.04, -0.6, "gold"); g.box(0.6, 0.08, 0.5, 0.2, 0.04, -0.9, "gold")
    for x, z in ((-1.7, 0.9), (-1.7, -0.9), (1.7, -0.9), (1.7, 0.9)):
        g.cyl(0.12, 0.12, 0.32, x, -0.14, z, "gold")
    return {}


def dev_bond(g):
    g.box(4, 0.3, 2.4, 0.4, -0.35, 0, "sub"); g.box(1.4, 0.4, 1.6, 1.2, 0.0, 0, "gaas")
    g.trace([(-1.6, 0.35), (0.2, 0.35)], 0.2, 0.05, -0.17, "gold"); g.trace([(-1.6, -0.35), (0.2, -0.35)], 0.2, 0.05, -0.17, "gold")
    g.box(0.25, 0.04, 0.25, 0.75, 0.22, 0.35, "gold"); g.box(0.25, 0.04, 0.25, 0.75, 0.22, -0.35, "gold")
    g.tube([(0.15, -0.15, 0.35), (0.35, 0.55, 0.35), (0.75, 0.24, 0.35)], 0.025, "gold")
    g.tube([(0.15, -0.15, -0.35), (0.35, 0.55, -0.35), (0.75, 0.24, -0.35)], 0.025, "gold")
    return dict(hmin=0.05)


def dev_xsec(g):
    g.box(2.4, 0.06, 4, 0, 0.62, 0, "copper", gnd=True); g.box(2.4, 0.06, 4, 0, -0.62, 0, "copper", gnd=True)
    g.box(2.4, 1.18, 4, 0, 0, 0, "sub"); g.box(0.5, 0.06, 4, 0, 0, 0, "copper")
    return dict(q2d=True, airpad=0.0)


def dev_wilk(g):
    g.box(4.4, 0.25, 3.2, 0, -0.14, 0, "sub"); g.box(4.4, 0.04, 3.2, 0, -0.29, 0, "copper", gnd=True)
    g.trace([(-2.2, 0), (-1.0, 0)], 0.18, 0.04, 0.0, "copper")
    arc = lambda s: [(-math.cos(math.pi * i / 10), s * 0.8 * math.sin(math.pi * i / 10)) for i in range(11)]
    g.trace(arc(1), 0.1, 0.04, 0.0, "copper"); g.trace(arc(-1), 0.1, 0.04, 0.0, "copper")
    g.box(0.18, 0.12, 0.3, 1.0, 0.04, 0, "resist")
    g.trace([(1.0, 0.1), (1.0, 0.7), (2.2, 0.7)], 0.14, 0.04, 0.0, "copper"); g.trace([(1.0, -0.1), (1.0, -0.7), (2.2, -0.7)], 0.14, 0.04, 0.0, "copper")
    return {}


def dev_sma(g):
    g.box(3.4, 0.2, 2.4, 0.6, -0.1, 0, "sub"); g.box(3.4, 0.04, 2.4, 0.6, -0.22, 0, "copper", gnd=True)
    g.trace([(-0.9, 0), (2.3, 0)], 0.22, 0.04, 0.02, "copper")
    g.box(0.25, 1.4, 1.4, -1.25, 0.1, 0, "gold")
    outer = g.occ.addCylinder(-2.75, 0.1, 0, 1.4, 0, 0, 0.42); inner = g.occ.addCylinder(-2.8, 0.1, 0, 1.5, 0, 0, 0.36)
    shell, _ = g.occ.cut([(3, outer)], [(3, inner)], removeTool=False)
    g.add(shell, "gold"); g.add([(3, inner)], "ptfe")
    g.cyl(0.07, 0.07, 2.2, -1.6, 0.08, 0, "gold", rot=(0, 0, math.pi / 2))
    return {}


def dev_cav(g):
    g.box(5, 0.08, 1.6, 0, 0.6, 0, "alu"); g.box(5, 0.08, 1.6, 0, -0.6, 0, "alu"); g.box(5, 1.2, 0.08, 0, 0, 0.8, "alu")
    for x in (-1.5, -0.5, 0.5, 1.5):
        g.box(0.08, 1.2, 0.5, x, 0, -0.5, "alu")
    for x in (-2, -1, 0, 1, 2):
        g.cyl(0.14, 0.14, 0.7, x, 0.25, 0, "alu")
    return dict(airpad=0.02)


def dev_meta(g):
    g.box(2, 0.3, 2, 0, -0.15, 0, "sub"); g.box(2, 0.04, 2, 0, -0.32, 0, "copper", gnd=True)
    for r1, r2, a0 in ((0.6, 0.07, 0.4), (0.38, 0.06, 0.4 + math.pi)):
        t = g.occ.addTorus(0, 0.03, 0, r1, r2, angle=math.pi * 1.75, zAxis=[0, 1, 0])
        g.occ.rotate([(3, t)], 0, 0.03, 0, 0, 1, 0, a0)
        g.add([(3, t)], "copper")
    return dict(radiate=True)


def dev_grating(g):
    g.box(5, 0.8, 2, 0, -0.6, 0, "oxide"); g.box(1.6, 0.22, 2, -1.7, -0.09, 0, "si")
    for i in range(9):
        g.box(0.13, 0.22, 2, -0.7 + i * 0.26, -0.09, 0, "si")
    g.box(1.6, 0.22, 0.4, 2.0, -0.09, 0, "si")
    g.cyl(0.35, 0.35, 2.2, 0.6, 1.4, 0, "glass", rot=(0, 0, 0.18))
    return dict(radiate=True)


def dev_patch(g):
    g.box(3, 0.25, 3, 0, -0.13, 0, "sub"); g.box(3, 0.04, 3, 0, -0.28, 0, "copper", gnd=True)
    g.box(1.4, 0.04, 1.1, 0, 0.02, 0, "copper"); g.trace([(0, 0.55), (0, 1.5)], 0.14, 0.04, 0.02, "copper")
    return dict(radiate=True)


def dev_yagi(g):
    g.cyl(0.04, 0.04, 5, 0, 1.2, 0, "alu", rot=(0, 0, math.pi / 2)); g.cyl(0.05, 0.05, 1.3, -0.4, 0.55, 0, "alu")
    for x, L in ((-2.2, 2.3), (-1.2, 2.15), (0, 2.0), (1.1, 1.9), (2.2, 1.8)):
        g.cyl(0.025, 0.025, L, x, 1.2, 0, "alu", rot=(math.pi / 2, 0, 0))
    return dict(radiate=True, hmin=0.07)


def dev_dish(g):
    occ = g.occ
    n, f, t = 14, 1.3, 0.05
    outer = [occ.addPoint(2.0 * i / n, (2.0 * i / n) ** 2 / (4 * f), 0) for i in range(n + 1)]
    inner = [occ.addPoint(2.0 * i / n, (2.0 * i / n) ** 2 / (4 * f) + t, 0) for i in range(n, -1, -1)]
    c1 = occ.addSpline(outer); c2 = occ.addLine(outer[-1], inner[0]); c3 = occ.addSpline(inner); c4 = occ.addLine(inner[-1], outer[0])
    s = occ.addPlaneSurface([occ.addCurveLoop([c1, c2, c3, c4])])
    rev = occ.revolve([(2, s)], 0, 0, 0, 0, 1, 0, 2 * math.pi)
    vols = [v for v in rev if v[0] == 3]
    occ.rotate(vols, 0, 0, 0, 1, 0, 0, -math.pi / 2)
    g.add(vols, "alu")
    g.cyl(0.08, 0.18, 0.4, 0, 0, 1.25, "alu", rot=(math.pi / 2, 0, 0))
    for a, b in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        g.tube([(a * 1.35, b * 1.35, 0.7), (a * 0.6, b * 0.6, 1.0), (a * 0.12, b * 0.12, 1.2)], 0.05, "alu")
    return dict(radiate=True, hmin=0.07)


def dev_gpr(g):
    g.box(4, 1.2, 3, 0, -0.9, 0, "soil"); g.cyl(0.18, 0.18, 2.6, 0.4, -1.0, 0, "steel", rot=(math.pi / 2, 0, 0))
    for s in (1, -1):
        g.prism([(0, 0), (s * 1.1, 0.5), (s * 1.1, -0.5)], "xz", 0.03, (s * 0.05, 0.235, 0), "copper")
    g.box(2.6, 0.04, 1.4, 0, 0.75, 0, "steel")
    return dict(radiate=True)


def dev_phone(g):
    g.sphere(1.1, 0, 0, 0, "tissue", scale=(0.85, 1.05, 1.0)); g.sphere(0.18, 0, 0, 1.0, "tissue", scale=(0.5, 1, 0.6))
    g.box(0.25, 2.4, 1.1, 0, -0.1, 1.45, "plastic", rot=(0, 0, -0.25)); g.box(0.05, 0.5, 0.8, -0.1, 0.95, 1.45, "copper", rot=(0, 0, -0.25))
    return dict(radiate=True)


def dev_mri(g):
    for x in (-1.4, 1.4):
        t = g.occ.addTorus(x, 0, 0, 1.2, 0.07, zAxis=[1, 0, 0]); g.add([(3, t)], "copper")
    for i in range(12):
        a = i * math.pi / 6 + math.pi / 12   # rungs offset from the seam of the torus
        g.cyl(0.06, 0.06, 2.8, 0, 1.2 * math.sin(a), 1.2 * math.cos(a), "copper", rot=(0, 0, math.pi / 2))
    g.cyl(0.55, 0.55, 3.4, 0.6, -0.3, 0, "tissue", rot=(0, 0, math.pi / 2)); g.sphere(0.42, -1.5, -0.25, 0, "tissue")
    return dict(radiate=True, hmin=0.06)


def dev_car(g):
    g.box(4.4, 0.9, 1.9, 0, 0.75, 0, "steel"); g.box(2.3, 0.7, 1.7, -0.2, 1.55, 0, "steel")
    g.box(0.06, 0.6, 1.6, 0.98, 1.5, 0, "glass", rot=(0, 0, 0.5))
    for x, z in ((-1.4, 0.95), (1.4, 0.95), (-1.4, -0.95), (1.4, -0.95)):
        g.cyl(0.38, 0.38, 0.25, x, 0.38, z, "plastic", rot=(math.pi / 2, 0, 0))
    g.cyl(0.05, 0.05, 0.6, -0.6, 2.2, 0, "steel")   # thicker than the page model so the mesher can resolve it
    return dict(radiate=True, hmin=0.08)


def dev_aircraft(g):
    g.cyl(0.32, 0.32, 4.4, 0, 0, 0, "alu", rot=(0, 0, math.pi / 2))
    g.cyl(0.0001, 0.32, 0.9, 2.65, 0, 0, "alu", rot=(0, 0, -math.pi / 2))
    g.cyl(0.1, 0.32, 0.9, -2.65, 0.08, 0, "alu", rot=(0, 0, math.pi / 2))
    def wing(L, root, tip, sweep):
        return [(0, 0), (-sweep, L), (-sweep - tip, L), (-root, 0)]
    for s in (1, -1):
        g.prism([(a, s * b) for a, b in wing(2.6, 1.3, 0.45, 0.9)], "xz", 0.06, (0.6, -0.08, s * 0.2), "alu")
        g.prism([(a, s * b) for a, b in wing(0.9, 0.6, 0.25, 0.35)], "xz", 0.06, (-2.4, 0.07, s * 0.1), "alu")
    g.prism(wing(0.9, 0.7, 0.3, 0.45), "xy", 0.06, (-2.3, 0.25, 0.0), "alu")
    return dict(plane=True)


def dev_ship(g):
    g.prism([(-3, -0.5), (2.4, -0.5), (3.2, 0), (2.4, 0.5), (-3, 0.5)], "xz", 0.7, (0, 0, 0), "steel")
    g.box(1.6, 0.6, 0.8, -0.6, 0.65 + 0.35, 0, "steel"); g.box(0.8, 0.4, 0.6, -0.6, 1.15 + 0.35, 0, "steel")
    g.cyl(0.07, 0.07, 1.2, -0.6, 1.9 + 0.35, 0, "steel"); g.box(0.5, 0.12, 0.12, -0.6, 2.2 + 0.35, 0, "steel"); g.box(0.5, 0.3, 0.4, 1.4, 0.5 + 0.35, 0, "steel")
    return dict(plane=True, hmin=0.09)


DEVICES = {"aip": dev_aip, "spiral": dev_spiral, "mmic": dev_mmic, "bond": dev_bond, "xsec": dev_xsec, "wilk": dev_wilk, "sma": dev_sma, "cav": dev_cav,
           "meta": dev_meta, "grating": dev_grating, "patch": dev_patch, "yagi": dev_yagi, "dish": dev_dish, "gpr": dev_gpr, "phone": dev_phone,
           "mri": dev_mri, "car": dev_car, "ac-vhf": dev_aircraft, "ac-x": dev_aircraft, "ship": dev_ship}
PLANAR_MOM25 = {"spiral", "mmic", "wilk", "patch"}


# ---------------------------------------------------------------- meshing
def r4(a):
    return [round(float(x), 3) for x in a]


def tri_block(node_tags, coords_of, tris):
    """Index a list of triangles (node tag triples) into compact v/i arrays."""
    used = {}
    v, idx = [], []
    for t in tris:
        for n in t:
            if n not in used:
                used[n] = len(used); v.extend(coords_of[n])
            idx.append(used[n])
    return {"v": r4(v), "i": idx}


def surface_tris(surfs):
    tris = []
    for s in surfs:
        types, _, nodes = gmsh.model.mesh.getElements(2, s)
        for ty, nd in zip(types, nodes):
            if ty == 2:
                tris.extend(np.array(nd, dtype=np.int64).reshape(-1, 3).tolist())
    return tris


def mesh_device(did, algo3d=10, heal=False):
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add(did)
    g = G()
    opts = DEVICES[did](g) or {}
    occ = g.occ
    # fuse the pieces of each part so that traces made of segments become one solid
    parts = []
    for vols, mat, gnd in g.parts:
        if len(vols) > 1:
            fused, _ = occ.fuse(vols[:1], vols[1:])
            vols = [v for v in fused if v[0] == 3]
        parts.append((vols, mat, gnd))
    if heal:
        occ.healShapes()
    occ.synchronize()
    xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(-1, -1)
    L = max(xmax - xmin, ymax - ymin, zmax - zmin)
    pad = opts.get("airpad", 0.35 * L if (opts.get("radiate") or opts.get("plane")) else 0.12 * L)
    air = occ.addBox(xmin - pad, ymin - pad, zmin - pad, xmax - xmin + 2 * pad, ymax - ymin + 2 * pad, zmax - zmin + 2 * pad)
    # fragment: one conformal mesh for all parts and the air
    inputs = [(3, air)] + [v for vols, _, _ in parts for v in vols]
    owner = [("air", False)] + [(mat, gnd) for vols, mat, gnd in parts for _ in vols]
    _, omap = occ.fragment(inputs, [])
    occ.synchronize()
    prio = lambda m: 2 if m in METAL else (0 if m == "air" else 1)
    volmat = {}
    for (mat, gnd), children in zip(owner, omap):
        for d, t in children:
            if d != 3: continue
            old = volmat.get(t)
            if old is None or prio(mat) > prio(old[0]) or (prio(mat) == prio(old[0]) and mat != "air"):
                volmat[t] = (mat, gnd)
    # mesh size: fine near metal, coarse in the air
    hmin = opts.get("hmin", L / 30); hmax = L / 7
    metal_surfs = []
    for t, (m, _) in volmat.items():
        if m in METAL:
            metal_surfs += [s for _, s in gmsh.model.getBoundary([(3, t)], oriented=False)]
    gmsh.option.setNumber("Mesh.MeshSizeMin", hmin * 0.5)
    gmsh.option.setNumber("Mesh.MeshSizeMax", hmax)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 6)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.option.setNumber("Mesh.Algorithm", 6)
    gmsh.option.setNumber("Mesh.Algorithm3D", algo3d)
    if metal_surfs:
        fd = gmsh.model.mesh.field.add("Distance"); gmsh.model.mesh.field.setNumbers(fd, "SurfacesList", metal_surfs)
        ft = gmsh.model.mesh.field.add("Threshold"); gmsh.model.mesh.field.setNumber(ft, "InField", fd)
        gmsh.model.mesh.field.setNumber(ft, "SizeMin", hmin); gmsh.model.mesh.field.setNumber(ft, "SizeMax", hmax)
        gmsh.model.mesh.field.setNumber(ft, "DistMin", 0); gmsh.model.mesh.field.setNumber(ft, "DistMax", L / 4)
        gmsh.model.mesh.field.setAsBackgroundMesh(ft)
    gmsh.model.mesh.generate(3)
    ntags, ncoords, _ = gmsh.model.mesh.getNodes()
    coords = {int(t): ncoords[3 * i:3 * i + 3] for i, t in enumerate(ntags)}

    # model surfaces: boundary triangles of each non-air volume, grouped by material
    mats, out_parts = [], []
    groups = {}
    for t, (m, gnd) in volmat.items():
        if m == "air": continue
        groups.setdefault((m, gnd), []).append(t)
    for (m, gnd), vols in groups.items():
        surfs = [s for _, s in gmsh.model.getBoundary([(3, t) for t in vols], oriented=False, combined=True)]
        out_parts.append({"mat": m, "gnd": gnd, **tri_block(None, coords, surface_tris(surfs))})
    air_vols = [t for t, (m, _) in volmat.items() if m == "air"]
    outer = [s for _, s in gmsh.model.getBoundary([(3, air)] if False else [(3, t) for t in volmat], oriented=False, combined=True)]
    air_block = tri_block(None, coords, surface_tris(outer))

    # FEM: tetrahedra, edges, and a crinkle cut through the middle (plane z = centre)
    tets, tetmat = [], []
    matlist = ["air"] + sorted({m for m, _ in volmat.values() if m != "air"})
    for t, (m, _) in volmat.items():
        types, _, nodes = gmsh.model.mesh.getElements(3, t)
        for ty, nd in zip(types, nodes):
            if ty == 4:
                arr = np.array(nd, dtype=np.int64).reshape(-1, 4)
                tets.append(arr); tetmat.append(np.full(len(arr), matlist.index(m)))
    tets = np.vstack(tets); tetmat = np.concatenate(tetmat)
    e = np.sort(np.vstack([tets[:, [a, b]] for a, b in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))]), axis=1)
    n_edges = len(np.unique(e, axis=0))
    tagidx = {t: i for i, t in enumerate(ntags.astype(np.int64))}
    P = ncoords.reshape(-1, 3)
    zc = (zmin + zmax) / 2
    zs = P[np.vectorize(tagidx.get)(tets)][:, :, 2]
    hit = (zs.min(axis=1) <= zc) & (zs.max(axis=1) >= zc)
    cut_tris, cut_m = [], []
    for row, m in zip(tets[hit], tetmat[hit]):
        for f in ((0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)):
            cut_tris.append([int(row[k]) for k in f]); cut_m.append(int(m))
    cut = tri_block(None, coords, cut_tris); cut["m"] = cut_m
    # slice: the intersection of each crossing tetrahedron with the plane (a triangle or a quad)
    sv, si, sm, se = [], [], [], []
    TE = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    for row, m in zip(tets[hit], tetmat[hit]):
        X = P[[tagidx[int(n)] for n in row]]
        pts = []
        for a, b in TE:
            za, zb = X[a, 2] - zc, X[b, 2] - zc
            if za == 0 and zb == 0: continue
            if (za <= 0 <= zb) or (zb <= 0 <= za):
                t = za / (za - zb) if za != zb else 0.0
                pts.append(X[a] + t * (X[b] - X[a]))
        if len(pts) < 3: continue
        pts = np.unique(np.round(np.array(pts), 6), axis=0)
        if len(pts) < 3: continue
        c = pts.mean(axis=0); ang = np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]); pts = pts[np.argsort(ang)]
        base = len(sv) // 3
        for q in pts: sv.extend([q[0], q[1], zc])
        for k in range(1, len(pts) - 1): si.extend([base, base + k, base + k + 1]); sm.append(int(m))
        for k in range(len(pts)): se.extend([base + k, base + (k + 1) % len(pts)])
    slice_ = {"v": r4(sv), "i": si, "m": sm, "e": se}
    fem = {"tets": int(len(tets)), "nodes": int(len(ntags)), "edges": int(n_edges), "mats": matlist, "cutz": round(zc, 4), "slice": slice_}

    # MoM: triangles on the metal surfaces (planar devices: only the top face of each non-ground metal)
    mom_tris = []
    for p_vols, (m, gnd) in [(v, k) for k, v in groups.items()]:
        if m not in METAL: continue
        if did in PLANAR_MOM25 and gnd: continue
        surfs = [s for _, s in gmsh.model.getBoundary([(3, t) for t in p_vols], oriented=False, combined=True)]
        tops = {}
        if did in PLANAR_MOM25:  # 2.5D: keep the top face of each metal sheet (flat in y, at the highest y of its volume)
            for t in p_vols:
                vy1 = gmsh.model.getBoundingBox(3, t)[4]
                for _, sf in gmsh.model.getBoundary([(3, t)], oriented=False):
                    b = gmsh.model.getBoundingBox(2, sf)
                    if abs(b[4] - b[1]) < 1e-6 and abs(b[4] - vy1) < 1e-6: tops[sf] = True
        for s in surfs:
            if did in PLANAR_MOM25 and s not in tops: continue
            mom_tris += surface_tris([s])
    te = {}
    for t in mom_tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2])):
            k = (min(a, b), max(a, b)); te[k] = te.get(k, 0) + 1
    kind = "metal"
    if not mom_tris:  # no metal (photonics, tissue): surface equivalence meshes the dielectric surfaces
        kind = "dielectric"
        for (m, gnd), p_vols in groups.items():
            mom_tris += surface_tris([s for _, s in gmsh.model.getBoundary([(3, t) for t in p_vols], oriented=False, combined=True)])
        te = {}
        for t in mom_tris:
            for a, b in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2])):
                k = (min(a, b), max(a, b)); te[k] = te.get(k, 0) + 1
    mom = {"kind": kind, "tris": len(mom_tris), "rwg": sum(1 for c in te.values() if c == 2), **tri_block(None, coords, mom_tris)}
    data = {"id": did, "bbox": r4([xmin, ymin, zmin, xmax, ymax, zmax]), "parts": out_parts, "air": air_block, "fem": fem, "mom": mom}
    gmsh.finalize()
    if opts.get("q2d"):
        data["q2d"] = mesh_q2d()
    return data


def mesh_q2d():
    """2D cross-section of the stripline (x-y plane), meshed with triangles."""
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0); gmsh.model.add("xs")
    occ = gmsh.model.occ
    rects = [("sub", occ.addRectangle(-1.2, -0.59, 0, 2.4, 1.18)), ("copper", occ.addRectangle(-1.2, 0.59, 0, 2.4, 0.06)),
             ("copper", occ.addRectangle(-1.2, -0.65, 0, 2.4, 0.06)), ("copper", occ.addRectangle(-0.25, -0.03, 0, 0.5, 0.06))]
    _, omap = occ.fragment([(2, t) for _, t in rects], []); occ.synchronize()
    sm = {}
    for (m, _), ch in zip(rects, omap):
        for d, t in ch:
            if d == 2 and (sm.get(t) is None or m == "copper"): sm[t] = m
    gmsh.option.setNumber("Mesh.MeshSizeMax", 0.2); gmsh.option.setNumber("Mesh.MeshSizeMin", 0.03)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 0)
    fd = gmsh.model.mesh.field.add("Distance"); gmsh.model.mesh.field.setNumbers(fd, "CurvesList", [c for _, c in gmsh.model.getBoundary([(2, t) for t, m in sm.items() if m == "copper"], oriented=False)])
    ft = gmsh.model.mesh.field.add("Threshold"); gmsh.model.mesh.field.setNumber(ft, "InField", fd)
    for k, v in (("SizeMin", 0.035), ("SizeMax", 0.2), ("DistMin", 0), ("DistMax", 0.6)): gmsh.model.mesh.field.setNumber(ft, k, v)
    gmsh.model.mesh.field.setAsBackgroundMesh(ft)
    gmsh.model.mesh.generate(2)
    ntags, nc, _ = gmsh.model.mesh.getNodes(); coords = {int(t): nc[3 * i:3 * i + 3] for i, t in enumerate(ntags)}
    tris, mm = [], []
    for t, m in sm.items():
        tt = surface_tris([t]); tris += tt; mm += [1 if m == "copper" else 0] * len(tt)
    blk = tri_block(None, coords, tris); blk["m"] = mm; blk["tris"] = len(tris)
    gmsh.finalize()
    return blk


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ids = sys.argv[1:] or list(DEVICES)
    for did in ids:
        d = None
        for algo, heal in ((10, False), (1, False), (4, False)):
            try:
                d = mesh_device(did, algo, heal); d["algo3d"] = {10: "HXT", 1: "Delaunay", 4: "Frontal"}[algo]; break
            except Exception as ex:  # try the next mesher
                print(f"{did}: algorithm {algo} (heal={heal}) failed: {str(ex)[:80]}")
                try: gmsh.finalize()
                except Exception: pass
        if d is None:
            print(f"{did}: FAILED"); continue
        path = os.path.join(OUT, f"{did}.json")
        with open(path, "w") as f:
            json.dump(d, f, separators=(",", ":"))
        print(f"{did}: {d['fem']['tets']} tets, {d['fem']['edges']} edges, MoM {d['mom']['tris']} tris / {d['mom']['rwg']} RWG, slice {len(d['fem']['slice']['m'])} tris, {os.path.getsize(path)//1024} kB [{d.get('algo3d')}]")
