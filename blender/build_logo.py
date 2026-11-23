"""Monta a cena da logo animada da Kodaris Byte.

Uso:
    blender -b --factory-startup --python blender/build_logo.py
Gera blender/kodaris_logo.blend. Para renderizar:
    blender -b blender/kodaris_logo.blend -a

Estrutura da animação (30 fps, 150 frames = 5 s):
    0-24    esfera de energia surge (escala com overshoot)
    10-60   filamentos de plasma acendem
    40-75   K aparece com um flash
    75-150  idle: pulso suave, K girando levemente
Fundo preto puro: no site use `mix-blend-mode: screen` para fundir com qualquer fundo escuro.
"""
import math
import os

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
FPS, END = 30, 150


def srgb(h, a=1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (*lin, a)


LAVENDER = srgb("#C8B8E8")
LAVENDER_MID = srgb("#A898C8")
VIOLET = srgb("#7A5FB0")
VIOLET_HOT = srgb("#9B6BFF")
DEEP = srgb("#483868")


# ---------------------------------------------------------------- helpers
def key(obj_or_socket, path, frame, value, interp="BEZIER"):
    setattr(obj_or_socket, path, value) if not isinstance(value, (tuple, list)) else setattr(obj_or_socket, path, value)
    obj_or_socket.keyframe_insert(path, frame=frame)


def set_interp(id_data, interp):
    ad = id_data.animation_data
    if not ad or not ad.action:
        return
    for fc in iter_fcurves(ad.action):
        for kp in fc.keyframe_points:
            kp.interpolation = interp


def iter_fcurves(action):
    # Blender 4.4+ usa actions em camadas (slots); mantém compat com fcurves antigas
    if hasattr(action, "layers") and action.layers:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    yield from bag.fcurves
    elif hasattr(action, "fcurves"):
        yield from action.fcurves


def node(nt, kind, loc, **inputs):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in inputs.items():
        n.inputs[k].default_value = v
    return n


# ---------------------------------------------------------------- scene
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)

scene.render.engine = "BLENDER_EEVEE"
scene.render.fps = FPS
scene.frame_start, scene.frame_end = 0, END
scene.render.resolution_x = scene.render.resolution_y = 1080
scene.render.film_transparent = False
scene.eevee.taa_render_samples = 64
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "AgX - Punchy" if "AgX - Punchy" in [
    i.identifier for i in scene.view_settings.bl_rna.properties["look"].enum_items] else "None"

world = bpy.data.worlds.new("Black")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0, 0, 0, 1)
bg.inputs["Strength"].default_value = 0
scene.world = world

# camera
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 50
cam = bpy.data.objects.new("Cam", cam_data)
cam.location = (0, -4.6, 0)
cam.rotation_euler = (math.radians(90), 0, 0)
scene.collection.objects.link(cam)
scene.camera = cam

# raiz que gira devagar (a esfera inteira)
root = bpy.data.objects.new("LogoRoot", None)
scene.collection.objects.link(root)


# ---------------------------------------------------------------- materiais
def mat_shell():
    """Casca da esfera: borda brilhante (fresnel), centro transparente."""
    m = bpy.data.materials.new("Shell")
    m.use_nodes = True
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (900, 0))
    lw = node(nt, "ShaderNodeLayerWeight", (-400, 0), Blend=0.35)
    pw = node(nt, "ShaderNodeMath", (-200, 0))
    pw.operation = "POWER"
    pw.inputs[1].default_value = 2.2
    nt.links.new(lw.outputs["Facing"], pw.inputs[0])
    ramp = node(nt, "ShaderNodeValToRGB", (0, 150))
    ramp.color_ramp.elements[0].color = DEEP
    ramp.color_ramp.elements[1].color = LAVENDER
    nt.links.new(pw.outputs[0], ramp.inputs[0])
    strength = node(nt, "ShaderNodeMath", (0, -100))
    strength.operation = "MULTIPLY"
    strength.name = "ShellStrength"
    strength.inputs[1].default_value = 3.0
    nt.links.new(pw.outputs[0], strength.inputs[0])
    em = node(nt, "ShaderNodeEmission", (300, 100))
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(strength.outputs[0], em.inputs["Strength"])
    tr = node(nt, "ShaderNodeBsdfTransparent", (300, -100))
    add = node(nt, "ShaderNodeAddShader", (600, 0))
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    return m


def mat_plasma():
    """Filamentos de plasma: cristas finas de um ruído 4D animado (W)."""
    m = bpy.data.materials.new("Plasma")
    m.use_nodes = True
    m.surface_render_method = "BLENDED"
    m.use_backface_culling = False
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (1400, 0))
    tc = node(nt, "ShaderNodeTexCoord", (-1000, 0))

    def ridge(y, scale, width, w_name):
        nz = node(nt, "ShaderNodeTexNoise", (-750, y), Scale=scale, Detail=3.0, Roughness=0.55, Distortion=0.6)
        nz.noise_dimensions = "4D"
        nz.name = w_name
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        sub = node(nt, "ShaderNodeMath", (-550, y))
        sub.operation = "SUBTRACT"
        sub.inputs[1].default_value = 0.5
        nt.links.new(nz.outputs["Fac"], sub.inputs[0])
        ab = node(nt, "ShaderNodeMath", (-400, y))
        ab.operation = "ABSOLUTE"
        nt.links.new(sub.outputs[0], ab.inputs[0])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.location = (-250, y)
        mr.inputs[1].default_value = 0.0
        mr.inputs[2].default_value = width
        mr.inputs[3].default_value = 1.0
        mr.inputs[4].default_value = 0.0
        nt.links.new(ab.outputs[0], mr.inputs[0])
        pw = node(nt, "ShaderNodeMath", (-80, y))
        pw.operation = "POWER"
        pw.inputs[1].default_value = 3.0
        nt.links.new(mr.outputs[0], pw.inputs[0])
        return pw

    a = ridge(250, 1.5, 0.014, "NoiseA")
    b = ridge(-150, 3.0, 0.008, "NoiseB")
    bmul = node(nt, "ShaderNodeMath", (80, -150))
    bmul.operation = "MULTIPLY"
    bmul.inputs[1].default_value = 0.4
    nt.links.new(b.outputs[0], bmul.inputs[0])
    mx = node(nt, "ShaderNodeMath", (250, 100))
    mx.operation = "MAXIMUM"
    nt.links.new(a.outputs[0], mx.inputs[0])
    nt.links.new(bmul.outputs[0], mx.inputs[1])

    ramp = node(nt, "ShaderNodeValToRGB", (450, 250))
    ramp.color_ramp.elements[0].color = VIOLET
    ramp.color_ramp.elements[1].color = LAVENDER
    ramp.color_ramp.elements[0].position = 0.35
    nt.links.new(mx.outputs[0], ramp.inputs[0])
    st = node(nt, "ShaderNodeMath", (450, -50))
    st.operation = "MULTIPLY"
    st.name = "PlasmaStrength"
    st.inputs[1].default_value = 14.0
    nt.links.new(mx.outputs[0], st.inputs[0])
    em = node(nt, "ShaderNodeEmission", (750, 150))
    nt.links.new(ramp.outputs["Color"], em.inputs["Color"])
    nt.links.new(st.outputs[0], em.inputs["Strength"])
    tr = node(nt, "ShaderNodeBsdfTransparent", (750, -100))
    add = node(nt, "ShaderNodeAddShader", (1100, 0))
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs["Surface"])
    return m


def mat_core():
    """Névoa volumétrica roxa no miolo da esfera."""
    m = bpy.data.materials.new("Core")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (400, 0))
    vol = node(nt, "ShaderNodeVolumePrincipled", (0, 0))
    vol.inputs["Density"].default_value = 0.0
    vol.inputs["Emission Color"].default_value = VIOLET
    vol.inputs["Emission Strength"].default_value = 0.1
    vol.name = "CoreVol"
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    return m


def mat_k():
    m = bpy.data.materials.new("K")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (600, 0))
    bsdf = node(nt, "ShaderNodeBsdfPrincipled", (0, 0))
    bsdf.inputs["Base Color"].default_value = LAVENDER_MID
    bsdf.inputs["Metallic"].default_value = 0.6
    bsdf.inputs["Roughness"].default_value = 0.25
    bsdf.inputs["Emission Color"].default_value = LAVENDER
    bsdf.inputs["Emission Strength"].default_value = 0.0
    bsdf.name = "KBsdf"
    nt.links.new(bsdf.outputs[0], out.inputs["Surface"])
    return m


# ---------------------------------------------------------------- geometria
def add_obj(name, mesh, parent=None, mat=None):
    o = bpy.data.objects.new(name, mesh)
    scene.collection.objects.link(o)
    if parent:
        o.parent = parent
    if mat:
        o.data.materials.append(mat)
    return o


def uv_sphere(name, r, segs=96, rings=48):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=r)
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(me)
    bm.free()
    return me


def strip(a, b, t, clip_a, clip_b):
    """Faixa de espessura t ao longo de a->b, recortada por duas retas (ponto, normal)."""
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    n = Vector((-d.y, d.x))
    pts = []
    for off in (t / 2, -t / 2):
        p0 = a + n * off
        for (cp, cn) in (clip_a, clip_b):
            cp, cn = Vector(cp), Vector(cn)
            s = (cp - p0).dot(cn) / d.dot(cn)
            pts.append(p0 + d * s)
    # ordem: lado+ (clipA, clipB), lado- (clipB, clipA)
    return [pts[0], pts[1], pts[3], pts[2]]


def k_mesh():
    H, T, DEPTH = 0.56, 0.21, 0.16
    bar_l, bar_r = -0.46, -0.46 + T
    polys = [
        [(bar_l, -H), (bar_r, -H), (bar_r, H), (bar_l, H)],
        # braço superior: do meio da haste até o topo direito
        strip((bar_r, -0.06), (0.40, H), T * 0.95,
              ((bar_r, 0), (1, 0)), ((0, H), (0, 1))),
        # perna inferior: do braço até a base direita
        strip((-0.02, 0.16), (0.44, -H), T * 0.95,
              ((0, 0.16), (0, 1)), ((0, -H), (0, 1))),
    ]
    me = bpy.data.meshes.new("K")
    bm = bmesh.new()
    for poly in polys:
        verts = [bm.verts.new((p[0], 0, p[1])) for p in poly]
        f = bm.faces.new(verts)
        f.normal_update()
        if f.normal.y > 0:
            f.normal_flip()
        ext = bmesh.ops.extrude_face_region(bm, geom=[f])
        nv = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=nv, vec=(0, DEPTH, 0))
    bmesh.ops.translate(bm, verts=bm.verts, vec=(0, -DEPTH / 2, 0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return me


shell = add_obj("Shell", uv_sphere("Shell", 1.0), root, mat_shell())
plasma = add_obj("Plasma", uv_sphere("Plasma", 0.96), root, mat_plasma())
plasma2 = add_obj("PlasmaInner", uv_sphere("PlasmaInner", 0.78, 64, 32), root, plasma.data.materials[0])
plasma2.rotation_euler = (0.7, 0.3, 1.1)
core = add_obj("Core", uv_sphere("Core", 0.9, 32, 16), root, mat_core())

K = add_obj("K", k_mesh(), None, mat_k())
bev = K.modifiers.new("Bevel", "BEVEL")
bev.width = 0.012
bev.segments = 3
bev.limit_method = "ANGLE"

# luz para dar brilho metálico ao K
for loc, energy, color in (((-2.5, -3, 2.5), 400, LAVENDER), ((2.5, -2, -1.5), 250, VIOLET_HOT)):
    ld = bpy.data.lights.new("L", "AREA")
    ld.energy, ld.size = energy, 2.0
    ld.color = color[:3]
    lo = bpy.data.objects.new("Light", ld)
    lo.location = loc
    scene.collection.objects.link(lo)
    tr = lo.constraints.new("TRACK_TO")
    tr.target = K

# ---------------------------------------------------------------- animação
def ease(id_data, interp="BEZIER", easing="AUTO"):
    ad = id_data.animation_data
    if ad and ad.action:
        for fc in iter_fcurves(ad.action):
            for kp in fc.keyframe_points:
                kp.interpolation = interp
                kp.easing = easing


# esfera surge com overshoot
root.scale = (0.001,) * 3
root.keyframe_insert("scale", frame=0)
root.scale = (1.08,) * 3
root.keyframe_insert("scale", frame=20)
root.scale = (1,) * 3
root.keyframe_insert("scale", frame=30)
# giro contínuo e lento da esfera
root.rotation_euler = (0, 0, 0)
root.keyframe_insert("rotation_euler", frame=0)
root.rotation_euler = (0.25, 0, math.radians(70))
root.keyframe_insert("rotation_euler", frame=END)

# W dos ruídos: filamentos "vivos"
pm = plasma.data.materials[0].node_tree
for name, speed in (("NoiseA", 1.6), ("NoiseB", 2.4)):
    w = pm.nodes[name].inputs["W"]
    w.default_value = 0.0
    w.keyframe_insert("default_value", frame=0)
    w.default_value = speed * END / FPS
    w.keyframe_insert("default_value", frame=END)

ps = pm.nodes["PlasmaStrength"].inputs[1]
for f, v in ((0, 0), (10, 0), (45, 6), (70, 9), (85, 3.5), (110, 4.5), (130, 3.2), (END, 4)):
    ps.default_value = v
    ps.keyframe_insert("default_value", frame=f)

ss = shell.data.materials[0].node_tree.nodes["ShellStrength"].inputs[1]
for f, v in ((0, 0), (18, 2.5), (32, 1.2), (70, 3), (90, 1.2), (115, 1.6), (135, 1.2), (END, 1.4)):
    ss.default_value = v
    ss.keyframe_insert("default_value", frame=f)

cv = core.data.materials[0].node_tree.nodes["CoreVol"].inputs["Emission Strength"]
for f, v in ((0, 0), (30, 0.1), (70, 0.4), (90, 0.12), (END, 0.15)):
    cv.default_value = v
    cv.keyframe_insert("default_value", frame=f)

# K: aparece de trás pra frente com flash
K.scale = (0.001,) * 3
K.keyframe_insert("scale", frame=40)
K.scale = (1.12,) * 3
K.keyframe_insert("scale", frame=66)
K.scale = (1,) * 3
K.keyframe_insert("scale", frame=78)
K.rotation_euler = (0, 0, math.radians(-90))
K.keyframe_insert("rotation_euler", frame=40)
K.rotation_euler = (0, 0, 0)
K.keyframe_insert("rotation_euler", frame=72)
K.rotation_euler = (0, 0, math.radians(10))
K.keyframe_insert("rotation_euler", frame=112)
K.rotation_euler = (0, 0, math.radians(-6))
K.keyframe_insert("rotation_euler", frame=END)

ke = K.data.materials[0].node_tree.nodes["KBsdf"].inputs["Emission Strength"]
for f, v in ((40, 0), (68, 5), (82, 0.45), (115, 0.7), (END, 0.5)):
    ke.default_value = v
    ke.keyframe_insert("default_value", frame=f)

# W linear (sem easing)
for mat in (plasma.data.materials[0],):
    ad = mat.node_tree.animation_data
    for fc in iter_fcurves(ad.action):
        if "NoiseA" in fc.data_path or "NoiseB" in fc.data_path:
            for kp in fc.keyframe_points:
                kp.interpolation = "LINEAR"
for fc in iter_fcurves(root.animation_data.action):
    if fc.data_path == "rotation_euler":
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"

# ---------------------------------------------------------------- compositor: bloom
scene.render.use_compositing = True
tree = bpy.data.node_groups.new("KodarisComp", "CompositorNodeTree")
tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
scene.compositing_node_group = tree
rl = tree.nodes.new("CompositorNodeRLayers")
rl.location = (-400, 0)
glare = tree.nodes.new("CompositorNodeGlare")
glare.location = (0, 0)
glare.inputs["Type"].default_value = "Bloom"
glare.inputs["Quality"].default_value = "High"
glare.inputs["Threshold"].default_value = 0.9
glare.inputs["Strength"].default_value = 0.45
glare.inputs["Size"].default_value = 0.6
go = tree.nodes.new("NodeGroupOutput")
go.location = (300, 0)
tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
tree.links.new(glare.outputs["Image"], go.inputs[0])

# ---------------------------------------------------------------- saída
if hasattr(scene.render.image_settings, "media_type"):  # Blender 5.x
    scene.render.image_settings.media_type = "VIDEO"
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "HIGH"
scene.render.filepath = os.path.join(HERE, "renders", "kodaris_logo_")  # Blender acrescenta 0000-0150.mp4

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "kodaris_logo.blend"))
print("SAVED", os.path.join(HERE, "kodaris_logo.blend"))
