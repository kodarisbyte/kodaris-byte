"""Logo animada da Kodaris Byte — recriação da logo original (assets/brand/logo-original-linkedin.png).

Membrana gelatinosa lavanda, com um K formado por feixes de fibras trançadas,
núcleo de vidro com brilhos e fios finos que escapam das pontas.

Uso:
    blender -b --factory-startup --python blender/build_logo.py
    blender -b blender/kodaris_logo.blend -a          # PNGs RGBA em renders/intro/

Animação (30 fps, 120 frames = 4 s), fundo transparente:
    0-30    membrana infla (com overshoot)
    14-72   fibras crescem formando o K (haste, braço, perna)
    48-96   fios soltos e arcos da membrana crescem
    60-120  núcleo acende, brilhos aparecem, assenta
O último frame é a logo estática.
"""
import math
import os
import random

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, END = 30, 120
rng = random.Random(7)


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


FIBER = lin("#A88CEB")
FIBER_HI = lin("#D6C4FF")
MEMBRANE = lin("#8E74D8")
MEMBRANE_RIM = lin("#C7B5F2")
CORE = lin("#7B5CD6")


# ------------------------------------------------------------------ util
def iter_fcurves(id_data):
    ad = id_data.animation_data
    if not ad or not ad.action:
        return
    action = ad.action
    if hasattr(action, "layers") and action.layers:  # actions em camadas (4.4+)
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves
    elif hasattr(action, "fcurves"):
        yield from action.fcurves


def keys(target, path, pairs):
    for f, v in pairs:
        setattr(target, path, v)
        target.keyframe_insert(path, frame=f)


def node(nt, kind, loc=(0, 0), **inputs):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in inputs.items():
        n.inputs[k].default_value = v
    return n


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    return m, m.node_tree


# ------------------------------------------------------------------ cena
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)

scene.render.engine = "BLENDER_EEVEE"
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 0, END
scene.render.resolution_x = scene.render.resolution_y = 1080
scene.render.film_transparent = True
scene.eevee.taa_render_samples = 64
scene.view_settings.view_transform = "Standard"

world = bpy.data.worlds.new("Ambient")
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = lin("#2A2040")
bg.inputs["Strength"].default_value = 0.6
scene.world = world

cam_data = bpy.data.cameras.new("Cam")
cam_data.type = "ORTHO"
cam_data.ortho_scale = 2.45
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (0, -6, 0)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.collection.objects.link(cam)
scene.camera = cam

for name, loc, energy, color, size in (
    ("Key", (-3, -4, 3), 320, (1.0, 0.95, 1.0), 3),
    ("Fill", (3.5, -3, -1), 220, FIBER[:3], 3),
    ("Rim", (0, 4, 2.5), 450, MEMBRANE_RIM[:3], 4),
):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy, ld.size, ld.color = energy, size, color
    lo = bpy.data.objects.new(name, ld)
    lo.location = loc
    lo.rotation_euler = (-Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(lo)

root = bpy.data.objects.new("LogoRoot", None)
scene.collection.objects.link(root)


# ------------------------------------------------------------------ materiais
def mat_membrane():
    m, nt = new_mat("Membrane")
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = True
    out = node(nt, "ShaderNodeOutputMaterial", (1000, 0))
    lw = node(nt, "ShaderNodeLayerWeight", (-600, 0), Blend=0.45)
    # alpha: leitoso no centro, mais denso na borda
    a = nt.nodes.new("ShaderNodeMapRange")
    a.inputs[3].default_value = 0.5
    a.inputs[4].default_value = 0.95
    nt.links.new(lw.outputs["Facing"], a.inputs[0])
    ramp = node(nt, "ShaderNodeValToRGB", (-350, 250))
    ramp.color_ramp.elements[0].color = MEMBRANE
    ramp.color_ramp.elements[1].color = MEMBRANE_RIM
    nt.links.new(lw.outputs["Facing"], ramp.inputs[0])
    em = node(nt, "ShaderNodeEmission", (0, 250), Strength=0.95)
    nt.links.new(ramp.outputs[0], em.inputs["Color"])
    gl = node(nt, "ShaderNodeBsdfGlossy", (0, 50), Roughness=0.18)
    gl.inputs["Color"].default_value = (0.03, 0.025, 0.04, 1)
    body = node(nt, "ShaderNodeAddShader", (250, 150))
    nt.links.new(em.outputs[0], body.inputs[0])
    nt.links.new(gl.outputs[0], body.inputs[1])
    tr = node(nt, "ShaderNodeBsdfTransparent", (250, -100))
    mix = node(nt, "ShaderNodeMixShader", (600, 0))
    fade = node(nt, "ShaderNodeMath", (300, -250))
    fade.operation = "MULTIPLY"
    fade.name = "Fade"
    fade.inputs[1].default_value = 1.0
    nt.links.new(a.outputs[0], fade.inputs[0])
    nt.links.new(fade.outputs[0], mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(body.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return m


def mat_fiber():
    m, nt = new_mat("Fiber")
    out = node(nt, "ShaderNodeOutputMaterial", (600, 0))
    lw = node(nt, "ShaderNodeLayerWeight", (-500, 0), Blend=0.5)
    ramp = node(nt, "ShaderNodeValToRGB", (-250, 0))
    ramp.color_ramp.elements[0].color = FIBER
    ramp.color_ramp.elements[1].color = FIBER_HI
    nt.links.new(lw.outputs["Facing"], ramp.inputs[0])
    p = node(nt, "ShaderNodeBsdfPrincipled", (100, 0), Roughness=0.32)
    p.inputs["Coat Weight"].default_value = 0.6
    p.inputs["Emission Strength"].default_value = 0.35
    p.name = "FiberBsdf"
    nt.links.new(ramp.outputs[0], p.inputs["Base Color"])
    nt.links.new(ramp.outputs[0], p.inputs["Emission Color"])
    nt.links.new(p.outputs[0], out.inputs["Surface"])
    return m


def mat_core():
    """Núcleo de vidro dentro de cada traço, com pontinhos de brilho."""
    m, nt = new_mat("Core")
    m.surface_render_method = "BLENDED"
    out = node(nt, "ShaderNodeOutputMaterial", (1100, 0))
    tc = node(nt, "ShaderNodeTexCoord", (-900, -200))
    vo = node(nt, "ShaderNodeTexVoronoi", (-650, -200), Scale=55.0)
    vo.voronoi_dimensions = "4D"
    vo.name = "Sparkle"
    nt.links.new(tc.outputs["Object"], vo.inputs["Vector"])
    dot = nt.nodes.new("ShaderNodeMapRange")
    dot.inputs[2].default_value = 0.09
    dot.inputs[3].default_value = 1.0
    dot.inputs[4].default_value = 0.0
    nt.links.new(vo.outputs["Distance"], dot.inputs[0])
    pick = node(nt, "ShaderNodeMath", (-400, -350))
    pick.operation = "GREATER_THAN"
    pick.inputs[1].default_value = 0.72
    nt.links.new(vo.outputs["Color"], pick.inputs[0])
    sp = node(nt, "ShaderNodeMath", (-200, -250))
    sp.operation = "MULTIPLY"
    nt.links.new(dot.outputs[0], sp.inputs[0])
    nt.links.new(pick.outputs[0], sp.inputs[1])
    spk = node(nt, "ShaderNodeMath", (0, -250))
    spk.operation = "MULTIPLY"
    spk.name = "SparkleStrength"
    spk.inputs[1].default_value = 12.0
    nt.links.new(sp.outputs[0], spk.inputs[0])
    sem = node(nt, "ShaderNodeEmission", (250, -250))
    sem.inputs["Color"].default_value = (0.95, 0.92, 1.0, 1)
    nt.links.new(spk.outputs[0], sem.inputs["Strength"])

    lw = node(nt, "ShaderNodeLayerWeight", (-400, 200), Blend=0.4)
    cem = node(nt, "ShaderNodeEmission", (0, 200))
    cem.inputs["Color"].default_value = CORE
    cs = node(nt, "ShaderNodeMath", (-150, 100))
    cs.operation = "MULTIPLY"
    cs.name = "CoreStrength"
    cs.inputs[1].default_value = 1.4
    nt.links.new(lw.outputs["Facing"], cs.inputs[0])
    nt.links.new(cs.outputs[0], cem.inputs["Strength"])
    gl = node(nt, "ShaderNodeBsdfGlossy", (0, 400), Roughness=0.25)
    gl.inputs["Color"].default_value = (0.08, 0.06, 0.12, 1)
    tr = node(nt, "ShaderNodeBsdfTransparent", (250, 50))
    a1 = node(nt, "ShaderNodeAddShader", (450, 250))
    nt.links.new(gl.outputs[0], a1.inputs[0])
    nt.links.new(cem.outputs[0], a1.inputs[1])
    a2 = node(nt, "ShaderNodeAddShader", (650, 100))
    nt.links.new(a1.outputs[0], a2.inputs[0])
    nt.links.new(tr.outputs[0], a2.inputs[1])
    a3 = node(nt, "ShaderNodeAddShader", (850, 0))
    nt.links.new(a2.outputs[0], a3.inputs[0])
    nt.links.new(sem.outputs[0], a3.inputs[1])
    nt.links.new(a3.outputs[0], out.inputs["Surface"])
    return m


M_MEMBRANE, M_FIBER, M_CORE = mat_membrane(), mat_fiber(), mat_core()


# ------------------------------------------------------------------ curvas
def curve_obj(name, splines, bevel, mat, parent=root):
    """splines: lista de listas de (Vector, raio)."""
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = bevel
    cu.bevel_resolution = 3
    cu.resolution_u = 10
    cu.use_fill_caps = True
    cu.bevel_factor_mapping_start = "SPLINE"
    cu.bevel_factor_mapping_end = "SPLINE"
    for pts in splines:
        sp = cu.splines.new("NURBS")
        sp.points.add(len(pts) - 1)
        for p, (co, r) in zip(sp.points, pts):
            p.co = (co.x, co.y, co.z, 1.0)
            p.radius = r
        sp.order_u = 4
        sp.use_endpoint_u = True
    o = bpy.data.objects.new(name, cu)
    o.data.materials.append(mat)
    o.parent = parent
    scene.collection.objects.link(o)
    return o


def P(x, z, y=0.0):
    return Vector((x, y, z))


# traços do K (medidos na logo original; membrana ~ raio 1)
STROKES = {
    "Haste": (P(-0.33, 0.62), P(-0.44, -0.80), 0.115, 24),
    "Braco": (P(-0.24, -0.06), P(0.62, 0.55), 0.10, 20),
    "Perna": (P(-0.20, 0.02), P(0.66, -0.70), 0.10, 20),
}


def profile(t):
    """Fuso: fino nas pontas, cheio no meio."""
    return max(0.0, math.sin(math.pi * min(max(t, 0), 1))) ** 0.6


def frame_of(a, b):
    d = (b - a).normalized()
    n1 = d.cross(Vector((0, 1, 0))).normalized()
    n2 = d.cross(n1).normalized()
    return d, n1, n2


def bundle(a, b, rmax, count):
    """Feixe de fibras trançadas ao longo de a->b, abrindo nas pontas."""
    d, n1, n2 = frame_of(a, b)
    L = (b - a).length
    out = []
    for _ in range(count):
        phi = rng.uniform(0, 2 * math.pi)
        rho = rng.uniform(0.35, 1.0)
        twist = rng.choice((-1, 1)) * rng.uniform(0.5, 1.1)
        fray = rng.uniform(0.6, 1.6)
        t0, t1 = -rng.uniform(0.02, 0.14), 1 + rng.uniform(0.02, 0.14)
        wob_f, wob_a = rng.uniform(2, 5), rng.uniform(0.01, 0.03)
        pts = []
        N = 30
        for k in range(N):
            t = t0 + (t1 - t0) * k / (N - 1)
            R = rmax * rho * (0.18 + profile(t)) + fray * max(0.0, -t, t - 1) * 0.45
            th = phi + twist * 2 * math.pi * t
            off = n1 * math.cos(th) + n2 * math.sin(th) * 0.8
            wob = n1 * math.sin(t * wob_f * math.pi + phi) * wob_a
            pts.append((a + d * (L * t) + off * R + wob, 0.25 + 0.75 * profile(t * 0.9 + 0.05)))
        out.append(pts)
    return out


def whisker(start, heading, length, curl, rad=0.92):
    """Fio solto que sai da ponta e se enrola, sem sair da membrana."""
    pts = []
    pos = Vector(start)
    ang = math.atan2(heading.z, heading.x)
    N = 26
    step = length / N
    for k in range(N):
        s = k / (N - 1)
        pts.append((pos.copy(), 1.0 - 0.85 * s))
        ang += curl * (0.4 + 1.6 * s) * step * 4
        pos = pos + Vector((math.cos(ang), 0, math.sin(ang))) * step
        pos.y = 0.08 * math.sin(s * 6 + start.x * 3)
        r = math.hypot(pos.x, pos.z)
        if r > rad:
            pos.x, pos.z = pos.x * rad / r, pos.z * rad / r
            ang += curl * 0.6
    return pts


def arc(a0, a1, r, wav):
    """Fio que corre por dentro da membrana."""
    pts = []
    N = 28
    for k in range(N):
        s = k / (N - 1)
        a = a0 + (a1 - a0) * s
        rr = r + wav * math.sin(s * math.pi * 3)
        pts.append((P(rr * math.cos(a), rr * math.sin(a), 0.35 * math.sin(s * math.pi) - 0.1),
                    0.25 + 0.75 * math.sin(math.pi * s)))
    return pts


fibers, cores = {}, {}
for name, (a, b, rmax, n) in STROKES.items():
    fibers[name] = curve_obj(f"K_{name}", bundle(a, b, rmax, n), 0.011, M_FIBER)
    core_pts = [(a + (b - a) * (k / 19), 0.15 + profile(k / 19)) for k in range(20)]
    cores[name] = curve_obj(f"Core_{name}", [core_pts], rmax * 0.62, M_CORE)

tips = []
for a, b, _, _ in STROKES.values():
    d = (b - a).normalized()
    tips += [(b, d), (a, -d)]
wh = []
for pt, d in tips:
    for _ in range(2):
        h = Vector((d.x + rng.uniform(-0.6, 0.6), 0, d.z + rng.uniform(-0.6, 0.6))).normalized()
        wh.append(whisker(pt, h, rng.uniform(0.35, 0.7), rng.choice((-1, 1)) * rng.uniform(0.6, 1.4)))
whiskers = curve_obj("Fios", wh, 0.012, M_FIBER)

arcs_spl = []
for _ in range(7):
    a0 = rng.uniform(0, 2 * math.pi)
    arcs_spl.append(arc(a0, a0 + rng.uniform(0.6, 1.2), rng.uniform(0.62, 0.82), rng.uniform(0.02, 0.06)))
arcs = curve_obj("Arcos", arcs_spl, 0.009, M_FIBER)

# membrana: icosfera deformada por ruído, achatada em profundidade
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5, radius=1.0)
membrane = bpy.context.active_object
membrane.name = "Membrana"
membrane.scale = (1.0, 0.55, 1.0)
for f in membrane.data.polygons:
    f.use_smooth = True
membrane.data.materials.append(M_MEMBRANE)
tex = bpy.data.textures.new("Wobble", "CLOUDS")
tex.noise_scale = 0.9
tex.noise_depth = 1
wob_ctrl = bpy.data.objects.new("WobbleCtrl", None)
scene.collection.objects.link(wob_ctrl)
disp = membrane.modifiers.new("Wobble", "DISPLACE")
disp.texture = tex
disp.texture_coords = "OBJECT"
disp.texture_coords_object = wob_ctrl
disp.strength = 0.16
membrane.parent = root

# ------------------------------------------------------------------ animação
keys(root, "scale", [(0, (0.001,) * 3), (22, (1.06,) * 3), (34, (0.98,) * 3), (44, (1,) * 3)])
keys(root, "rotation_euler", [(0, (0, math.radians(-14), 0)), (60, (0, 0, 0)), (END, (0, math.radians(3), 0))])
keys(wob_ctrl, "location", [(0, (0, 0, 0)), (END, (0.5, 0.3, -0.4))])
for fc in iter_fcurves(wob_ctrl):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR"

keys(M_MEMBRANE.node_tree.nodes["Fade"].inputs[1], "default_value", [(0, 0.0), (18, 1.0)])

for obj, f0, f1 in ((fibers["Haste"], 14, 52), (fibers["Braco"], 28, 64), (fibers["Perna"], 34, 72),
                    (whiskers, 50, 96), (arcs, 48, 90)):
    keys(obj.data, "bevel_factor_end", [(0, 0.0), (f0, 0.0), (f1, 1.0)])
for name, (f0, f1) in (("Haste", (20, 58)), ("Braco", (34, 70)), ("Perna", (40, 76))):
    keys(cores[name].data, "bevel_factor_end", [(0, 0.0), (f0, 0.0), (f1, 1.0)])

core_nt = M_CORE.node_tree
keys(core_nt.nodes["CoreStrength"].inputs[1], "default_value", [(0, 0), (60, 0.6), (84, 3.0), (104, 1.4), (END, 1.4)])
keys(core_nt.nodes["SparkleStrength"].inputs[1], "default_value", [(0, 0), (66, 0), (90, 14), (END, 10)])
keys(core_nt.nodes["Sparkle"].inputs["W"], "default_value", [(0, 0.0), (END, 1.2)])
keys(M_FIBER.node_tree.nodes["FiberBsdf"].inputs["Emission Strength"], "default_value",
     [(0, 0.3), (70, 0.5), (84, 1.3), (104, 0.6), (END, 0.6)])

# ------------------------------------------------------------------ saída
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
os.makedirs(os.path.join(HERE, "renders", "intro"), exist_ok=True)
scene.render.filepath = os.path.join(HERE, "renders", "intro", "")
scene.frame_set(END)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "kodaris_logo.blend"))
print("SAVED")
