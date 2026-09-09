import bpy
import math
import os
from mathutils import Vector

# ============================================================
# NAVRAKSHAK CINEMATIC VESSEL BUILDER — V2.1
# Blender 5.2.x LTS compatible
#
# Goal: realistic maritime work / rescue / monitoring vessel
# inspired by the user's reference image.
#
# The complete cinematic scene contains ocean, lighting, sky,
# geofence and camera. ONLY NAVRAKHSHAK_VESSEL is exported to GLB
# so the website can supply its own interactive ocean + telemetry.
# ============================================================

OUT_DIR = os.path.join(os.path.expanduser('~'), 'Downloads', 'NavRakhshak_Blender')
os.makedirs(OUT_DIR, exist_ok=True)

OUT = os.path.join(OUT_DIR, 'navrakshak_vessel.glb')
BLEND_OUT = os.path.join(OUT_DIR, 'navrakshak_cinematic.blend')
PREVIEW_OUT = os.path.join(OUT_DIR, 'navrakshak_preview.png')

if os.path.exists(OUT):
    base, ext = os.path.splitext(OUT)
    i = 2
    while os.path.exists(f'{base}_{i}{ext}'):
        i += 1
    OUT = f'{base}_{i}{ext}'


def safe_set(obj, attr, value):
    try:
        setattr(obj, attr, value)
    except Exception:
        pass


def material(name, color, metallic=0.0, roughness=0.4, emission=None, emission_strength=4.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1.0)
    bs = m.node_tree.nodes.get('Principled BSDF')
    if bs:
        if 'Base Color' in bs.inputs:
            bs.inputs['Base Color'].default_value = (*color, 1.0)
        if 'Metallic' in bs.inputs:
            bs.inputs['Metallic'].default_value = metallic
        if 'Roughness' in bs.inputs:
            bs.inputs['Roughness'].default_value = roughness
        if emission and 'Emission Color' in bs.inputs:
            bs.inputs['Emission Color'].default_value = (*emission, 1.0)
        if emission and 'Emission Strength' in bs.inputs:
            bs.inputs['Emission Strength'].default_value = emission_strength
    return m


def cube(name, loc, scale, mat, bevel=0.0, parent=None, rotation=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    if rotation:
        o.rotation_euler = rotation
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('Edge Softening', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def cyl(name, loc, radius, depth, mat, verts=24, parent=None, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if rotation:
        o.rotation_euler = rotation
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def uv_sphere(name, loc, scale, mat, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def torus(name, loc, major, minor, mat, parent=None, rotation=None, segments=48):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, major_segments=segments, location=loc)
    o = bpy.context.object
    o.name = name
    if rotation:
        o.rotation_euler = rotation
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def beam_between(name, a, b, radius, mat, parent=None, verts=16):
    a = Vector(a)
    b = Vector(b)
    mid = (a + b) * 0.5
    length = (b - a).length
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=length, location=mid)
    o = bpy.context.object
    o.name = name
    o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def look_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def create_text(name, body, loc, size, mat, parent=None, rotation=(math.pi / 2, 0, 0)):
    bpy.ops.object.text_add(location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    o.data.body = body
    o.data.align_x = 'CENTER'
    o.data.align_y = 'CENTER'
    o.data.size = size
    o.data.extrude = 0.008
    o.data.bevel_depth = 0.002
    o.data.materials.append(mat)
    if parent:
        o.parent = parent
    return o


def make_hull(parent, hull_mat, lower_mat, stripe_mat):
    # 18m-class vessel. X is length, Y is beam, Z is vertical.
    stations = [
        (-9.2, 0.10, -1.10, 0.05),
        (-8.7, 1.15, -1.28, 0.12),
        (-7.4, 2.00, -1.52, 0.20),
        (-5.2, 2.30, -1.62, 0.34),
        (-2.0, 2.38, -1.68, 0.42),
        ( 1.8, 2.35, -1.66, 0.40),
        ( 5.0, 2.18, -1.54, 0.34),
        ( 7.3, 1.95, -1.35, 0.24),
        ( 8.7, 1.48, -1.08, 0.14),
        ( 9.2, 0.85, -0.72, 0.08),
    ]
    verts, faces = [], []
    for x, w, bottom, deck in stations:
        verts.extend([
            (x, 0.0, bottom),
            (x, w * 0.72, bottom + 0.10),
            (x, w, deck - 0.02),
            (x, w * 0.92, deck + 0.08),
            (x, -w * 0.92, deck + 0.08),
            (x, -w, deck - 0.02),
            (x, -w * 0.72, bottom + 0.10),
        ])
    for i in range(len(stations) - 1):
        a = i * 7
        b = (i + 1) * 7
        for j in range(6):
            faces.append((a + j, b + j, b + j + 1, a + j + 1))
    faces.append(tuple(range(6, -1, -1)))
    end = (len(stations) - 1) * 7
    faces.append(tuple(end + j for j in range(7)))
    me = bpy.data.meshes.new('NavRakhshak Hull Mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    hull = bpy.data.objects.new('Main Hull', me)
    bpy.context.collection.objects.link(hull)
    hull.data.materials.append(hull_mat)
    hull.parent = parent
    for p in me.polygons:
        p.use_smooth = True
    bevel = hull.modifiers.new('Hull Bevel', 'BEVEL')
    bevel.width = 0.10
    bevel.segments = 3

    # Dark lower boot stripe, following the hull visually.
    cube('Lower Hull Band', (0, 0, -1.10), (7.9, 2.33, 0.16), lower_mat, 0.08, parent)
    cube('Rescue Waterline Stripe', (0, 0, -0.88), (8.0, 2.30, 0.045), stripe_mat, 0.02, parent)
    return hull


def make_ocean(water_mat):
    size, n = 180.0, 110
    verts, faces = [], []
    for j in range(n + 1):
        y = (j / n - 0.5) * size
        for i in range(n + 1):
            x = (i / n - 0.5) * size
            z = (
                -1.25
                + 0.28 * math.sin(x * 0.11 + y * 0.09)
                + 0.14 * math.sin(x * 0.27 - y * 0.19)
                + 0.07 * math.cos((x + y) * 0.53)
                + 0.035 * math.sin(x * 0.91 + y * 0.72)
            )
            verts.append((x, y, z))
    for j in range(n):
        for i in range(n):
            a = j * (n + 1) + i
            faces.append((a, a + 1, a + n + 2, a + n + 1))
    me = bpy.data.meshes.new('Cinematic Ocean Mesh')
    me.from_pydata(verts, [], faces)
    me.update()
    ocean = bpy.data.objects.new('Ocean', me)
    bpy.context.collection.objects.link(ocean)
    ocean.data.materials.append(water_mat)
    for p in me.polygons:
        p.use_smooth = True

    ocean.shape_key_add(name='Basis')
    wave = ocean.shape_key_add(name='Wave_Swell')
    for v in wave.data:
        v.co.z += 0.15 * math.sin(v.co.x * 0.15 + v.co.y * 0.11)
    for frame, value in ((1, 0.0), (40, 1.0), (80, 0.0), (120, -0.55), (160, 0.0), (200, 1.0), (240, 0.0)):
        wave.value = value
        wave.keyframe_insert(data_path='value', frame=frame)
    return ocean


def setup_water():
    m = material('Ocean Water', (0.006, 0.045, 0.085), 0.30, 0.13)
    nt = m.node_tree
    nodes = nt.nodes
    links = nt.links
    bs = nodes.get('Principled BSDF')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 0.55
    noise.inputs['Detail'].default_value = 7.0
    noise.inputs['Roughness'].default_value = 0.72
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.28
    bump.inputs['Distance'].default_value = 0.20
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.002, 0.018, 0.035, 1)
    ramp.color_ramp.elements[1].color = (0.01, 0.16, 0.26, 1)
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    if 'Metallic' in bs.inputs: bs.inputs['Metallic'].default_value = 0.25
    if 'Roughness' in bs.inputs: bs.inputs['Roughness'].default_value = 0.13
    if 'IOR' in bs.inputs: bs.inputs['IOR'].default_value = 1.333
    if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value = 0.30
    if 'Coat Roughness' in bs.inputs: bs.inputs['Coat Roughness'].default_value = 0.08
    return m


def make_wake(parent, side, foam_mat):
    cu = bpy.data.curves.new('Wake Foam Curve', 'CURVE')
    cu.dimensions = '3D'
    cu.bevel_depth = 0.12
    cu.bevel_resolution = 5
    sp = cu.splines.new('BEZIER')
    sp.bezier_points.add(4)
    points = [
        (7.4, side * 0.75, -1.05),
        (9.5, side * 1.15, -1.08),
        (12.0, side * 1.70, -1.12),
        (15.0, side * 2.50, -1.18),
        (19.0, side * 3.40, -1.20),
    ]
    for bp, co in zip(sp.bezier_points, points):
        bp.co = co
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    o = bpy.data.objects.new('Wake Foam', cu)
    bpy.context.collection.objects.link(o)
    cu.materials.append(foam_mat)
    o.parent = parent
    return o


def make_deck_equipment(root, mats):
    navy, white, orange, dark, glass, cyan, rubber, yellow = mats

    # Raised working deck and bow deck.
    cube('Main Working Deck', (0, 0, 0.56), (7.85, 2.05, 0.16), dark, 0.10, root)
    cube('Raised Bow Deck', (-6.5, 0, 0.86), (2.0, 1.72, 0.18), white, 0.12, root)
    cube('Aft Working Deck', (5.8, 0, 0.76), (2.4, 1.90, 0.16), dark, 0.08, root)

    # Safety stripe / deck edge.
    cube('Orange Safety Rail Band', (0, -2.02, 0.73), (7.8, 0.045, 0.055), orange, 0.015, root)
    cube('Orange Safety Rail Band P', (0, 2.02, 0.73), (7.8, 0.045, 0.055), orange, 0.015, root)

    # Side rails.
    for y in (-2.03, 2.03):
        posts = (-7.5, -6.0, -4.0, -2.0, 0.0, 2.2, 4.5, 6.5, 8.0)
        for x in posts:
            cyl('Guardrail Post', (x, y, 1.15), 0.035, 0.82, white, 12, root)
        beam_between('Guardrail Top', (-7.5, y, 1.55), (8.0, y, 1.55), 0.035, white, root, 12)
        beam_between('Guardrail Mid', (-7.5, y, 1.22), (8.0, y, 1.22), 0.022, white, root, 10)

    # Mooring bollards.
    for x in (-7.8, -6.7, 6.8, 7.8):
        cyl('Mooring Bollard', (x, -1.2, 0.90), 0.12, 0.28, dark, 20, root)
        cyl('Mooring Bollard', (x, 1.2, 0.90), 0.12, 0.28, dark, 20, root)

    # Bow anchor/windlass.
    cyl('Anchor Windlass', (-7.15, 0, 1.05), 0.22, 1.8, dark, 24, root, rotation=(0, math.pi / 2, 0))
    cyl('Anchor Drum', (-7.15, 0, 1.28), 0.30, 0.18, yellow, 32, root, rotation=(0, math.pi / 2, 0))
    beam_between('Anchor Arm', (-7.8, 0, 0.85), (-9.0, 0, -0.35), 0.045, dark, root)

    # Two industrial winches / reels.
    for x, y in ((3.0, 0.0), (5.2, 0.0)):
        cyl('Deck Winch', (x, y, 1.05), 0.55, 0.65, dark, 32, root, rotation=(0, math.pi / 2, 0))
        torus('Winch Drum', (x, y, 1.05), 0.50, 0.075, yellow, root, rotation=(0, math.pi / 2, 0))
        cyl('Winch Hub', (x, y, 1.05), 0.16, 0.82, orange, 24, root, rotation=(0, math.pi / 2, 0))

    # Crate / equipment cases.
    for x, y, z in ((-3.8, -1.0, 1.0), (-2.8, 1.0, 1.0), (1.0, 1.0, 1.0)):
        cube('Deck Equipment Case', (x, y, z), (0.55, 0.45, 0.35), navy, 0.08, root)
        cube('Case Marking', (x, y - 0.46, z), (0.28, 0.018, 0.10), orange, 0.01, root)

    # Life rings.
    for x, y in ((-4.7, -2.12), (-1.2, 2.12), (5.7, -2.12)):
        torus('Life Ring', (x, y, 1.35), 0.32, 0.085, orange, root, rotation=(math.pi / 2, 0, 0), segments=32)

    # Fenders.
    for y in (-2.25, 2.25):
        for x in (-6.5, -3.5, 0, 3.5, 6.5):
            uv_sphere('Rubber Fender', (x, y, 0.15), (0.42, 0.16, 0.22), rubber, root)


def make_superstructure(root, mats):
    navy, white, orange, dark, glass, cyan, rubber, yellow = mats

    # Main bridge block.
    cube('Bridge Base', (-1.8, 0, 1.62), (2.45, 1.70, 1.02), white, 0.16, root)
    cube('Bridge Upper', (-1.25, 0, 2.62), (2.10, 1.60, 0.55), navy, 0.12, root)

    # Sloped-looking front glazing and side glazing.
    cube('Bridge Front Glass', (-3.38, 0, 2.72), (0.06, 1.28, 0.42), glass, 0.02, root, rotation=(0, math.radians(-8), 0))
    cube('Bridge Port Glass', (-1.30, 1.63, 2.68), (1.40, 0.045, 0.38), glass, 0.02, root)
    cube('Bridge Starboard Glass', (-1.30, -1.63, 2.68), (1.40, 0.045, 0.38), glass, 0.02, root)

    # Bridge roof and orange rescue accent.
    cube('Bridge Roof', (-1.25, 0, 3.25), (2.25, 1.82, 0.15), orange, 0.07, root)
    cube('Bridge Roof Cap', (-1.25, 0, 3.42), (1.55, 1.25, 0.06), white, 0.03, root)

    # Rear operations block.
    cube('Operations Block', (1.5, 0, 1.70), (1.35, 1.55, 1.10), navy, 0.13, root)
    cube('Operations Window Port', (1.5, 1.57, 2.05), (0.85, 0.04, 0.35), glass, 0.02, root)
    cube('Operations Window Starboard', (1.5, -1.57, 2.05), (0.85, 0.04, 0.35), glass, 0.02, root)

    # Funnel/exhaust structures.
    for y in (-0.70, 0.70):
        cube('Exhaust Stack', (2.55, y, 3.15), (0.42, 0.38, 1.05), dark, 0.10, root)
        cyl('Exhaust Cap', (2.55, y, 4.25), 0.44, 0.12, dark, 24, root)
        cube('Funnel Rescue Stripe', (2.55, y, 3.55), (0.44, 0.40, 0.12), orange, 0.02, root)

    # Rear mast platform.
    cube('Mast Platform', (2.7, 0, 4.55), (1.10, 1.0, 0.10), dark, 0.04, root)

    # Main communications mast.
    cyl('Main Communications Mast', (0.2, 0, 5.25), 0.11, 4.0, white, 20, root)
    cyl('Mast Collar', (0.2, 0, 3.45), 0.24, 0.10, orange, 24, root)
    beam_between('Mast Yardarm', (-1.15, 0, 6.15), (1.55, 0, 6.15), 0.055, white, root)
    beam_between('Mast Rear Brace', (0.2, 0, 4.0), (1.9, 0, 5.8), 0.045, white, root)

    # Radar scanner and pedestal.
    cyl('Radar Pedestal', (0.2, 0, 6.15), 0.16, 0.35, dark, 24, root)
    radar = cube('Radar Scanner', (0.2, 0, 6.38), (1.25, 0.10, 0.07), cyan, 0.025, root)
    radar.keyframe_insert(data_path='rotation_euler', frame=1)
    radar.rotation_euler.z = math.tau
    radar.keyframe_insert(data_path='rotation_euler', frame=120)
    radar.rotation_euler.z = math.tau * 2
    radar.keyframe_insert(data_path='rotation_euler', frame=240)

    # Satellite communication dish.
    torus('Satellite Dish Rim', (1.05, -0.65, 5.75), 0.55, 0.055, white, root, rotation=(math.radians(70), 0, math.radians(18)))
    cyl('Satellite Dish Feed', (1.05, -0.65, 6.05), 0.035, 0.60, cyan, 16, root, rotation=(math.radians(70), 0, math.radians(18)))

    # Small antenna cluster.
    for x, y, h in ((-0.65, 0.0, 0.9), (0.85, 0.85, 0.75), (0.85, -0.85, 0.75)):
        cyl('Comms Antenna', (x, y, 5.95), 0.035, h, white, 12, root)

    # Search light and navigation lights.
    cube('Search Light', (-2.7, 0, 3.72), (0.25, 0.32, 0.20), yellow, 0.04, root)
    for y, col in ((-1.70, orange), (1.70, cyan)):
        cyl('Bridge Nav Light', (-2.7, y, 3.65), 0.08, 0.16, col, 20, root)

    # Emergency beacon stack.
    cyl('Emergency Beacon Base', (0.2, 0, 6.9), 0.11, 0.18, dark, 20, root)
    cyl('Emergency Beacon', (0.2, 0, 7.12), 0.16, 0.24, orange, 24, root)

    # Text marking on side.
    create_text('Vessel Marking', 'NAVRAKSHAK', (2.2, -1.73, 1.55), 0.30, orange, root, rotation=(math.pi / 2, 0, 0))


def make_crane(root, dark_mat, orange_mat):
    # Compact rescue / recovery crane on aft deck.
    beam_between('Crane Base Post', (5.6, 0, 1.0), (5.6, 0, 3.4), 0.13, dark_mat, root)
    beam_between('Crane Boom', (5.6, 0, 3.35), (8.0, 0, 4.55), 0.11, dark_mat, root)
    beam_between('Crane Brace', (5.6, 0, 3.25), (7.4, 0, 4.35), 0.055, orange_mat, root)
    cyl('Crane Pivot', (5.6, 0, 3.35), 0.20, 0.30, orange_mat, 24, root, rotation=(math.pi / 2, 0, 0))
    beam_between('Crane Cable', (8.0, 0, 4.55), (8.0, 0, 1.35), 0.025, dark_mat, root)
    torus('Crane Hook', (8.0, 0, 1.25), 0.15, 0.035, orange_mat, root, rotation=(math.pi / 2, 0, 0), segments=24)


def make_ocean_foam(root, foam_mat):
    # Short foam ribbons hugging the hull.
    for side in (-1, 1):
        cu = bpy.data.curves.new('Hull Foam', 'CURVE')
        cu.dimensions = '3D'
        cu.bevel_depth = 0.055
        cu.bevel_resolution = 3
        sp = cu.splines.new('BEZIER')
        sp.bezier_points.add(4)
        pts = [
            (-7.5, side * 2.18, -1.08),
            (-4.0, side * 2.36, -1.12),
            (0.0, side * 2.40, -1.14),
            (4.0, side * 2.30, -1.10),
            (7.2, side * 2.05, -1.04),
        ]
        for bp, co in zip(sp.bezier_points, pts):
            bp.co = co
            bp.handle_left_type = 'AUTO'
            bp.handle_right_type = 'AUTO'
        o = bpy.data.objects.new('Hull Water Foam', cu)
        bpy.context.collection.objects.link(o)
        cu.materials.append(foam_mat)
        o.parent = root


def setup_world():
    world = bpy.context.scene.world or bpy.data.worlds.new('NavRakhshak Maritime World')
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    sky = nt.nodes.new('ShaderNodeTexSky')
    safe_set(sky, 'sky_type', 'MULTIPLE_SCATTERING')
    safe_set(sky, 'sun_elevation', math.radians(18))
    safe_set(sky, 'sun_rotation', math.radians(145))
    safe_set(sky, 'sun_intensity', 0.75)
    safe_set(sky, 'sun_size', math.radians(0.55))
    safe_set(sky, 'turbidity', 3.0)
    safe_set(sky, 'ground_albedo', 0.18)
    bg.inputs['Strength'].default_value = 0.28
    nt.links.new(sky.outputs['Color'], bg.inputs['Color'])
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def add_lighting():
    bpy.ops.object.light_add(type='SUN', location=(-30, -25, 30))
    sun = bpy.context.object
    sun.name = 'Maritime Sun'
    sun.data.energy = 4.5
    sun.data.angle = math.radians(3.5)
    sun.rotation_euler = (math.radians(28), math.radians(-20), math.radians(-38))

    bpy.ops.object.light_add(type='AREA', location=(-15, -18, 20))
    key = bpy.context.object
    key.name = 'Warm Maritime Key'
    key.data.energy = 1800
    key.data.shape = 'DISK'
    key.data.size = 16
    key.data.color = (1.0, 0.42, 0.18)
    look_at(key, (0, 0, 1))

    bpy.ops.object.light_add(type='AREA', location=(15, 14, 10))
    fill = bpy.context.object
    fill.name = 'Cool Ocean Fill'
    fill.data.energy = 1200
    fill.data.size = 14
    fill.data.color = (0.05, 0.32, 1.0)
    look_at(fill, (0, 0, 1))

    bpy.ops.object.light_add(type='AREA', location=(3, -18, 8))
    rim = bpy.context.object
    rim.name = 'Blue Vessel Rim'
    rim.data.energy = 1000
    rim.data.size = 10
    rim.data.color = (0.02, 0.30, 1.0)
    look_at(rim, (1, 0, 1.2))

    sunmat = material('Cinematic Sun Glow', (1.0, 0.20, 0.035), 0, 0.25, (1.0, 0.08, 0.01), 10)
    uv_sphere('Cinematic Sun Disc', (-48, 40, 32), (4.8, 4.8, 4.8), sunmat)


def add_geofence(cyan):
    for radius in (12, 22, 34, 48):
        torus('Tactical Range Ring', (0, 0, -1.00), radius, 0.035, cyan, segments=96)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=22, depth=5, location=(0, 0, 1.2))
    gf = bpy.context.object
    gf.name = '3D GEOFENCE'
    gf.display_type = 'WIRE'
    gf.data.materials.append(cyan)
    torus('GEOFENCE INNER', (0, 0, 3.8), 22, 0.045, cyan, segments=128)


def add_camera():
    bpy.ops.object.camera_add(location=(30, -34, 20))
    cam = bpy.context.object
    cam.name = 'Cinematic Camera'
    bpy.context.scene.camera = cam
    cam.data.lens = 52
    cam.data.sensor_width = 36
    look_at(cam, (0, 0, 0.8))
    cam.keyframe_insert(data_path='location', frame=1)
    cam.keyframe_insert(data_path='rotation_euler', frame=1)

    cam.location = (18, -28, 11)
    look_at(cam, (1, 0, 1.3))
    cam.keyframe_insert(data_path='location', frame=80)
    cam.keyframe_insert(data_path='rotation_euler', frame=80)

    cam.location = (-16, -23, 8)
    look_at(cam, (-1, 0, 1.3))
    cam.keyframe_insert(data_path='location', frame=160)
    cam.keyframe_insert(data_path='rotation_euler', frame=160)

    cam.location = (30, -34, 20)
    look_at(cam, (0, 0, 0.8))
    cam.keyframe_insert(data_path='location', frame=240)
    cam.keyframe_insert(data_path='rotation_euler', frame=240)


def build():
    print('')
    print('============================================================')
    print(' NAVRAKSHAK V2.1 REALISTIC MARITIME BUILDER')
    print('============================================================')

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    # Materials.
    navy = material('Nav Navy', (0.008, 0.045, 0.10), 0.65, 0.20)
    white = material('Marine White', (0.68, 0.76, 0.80), 0.28, 0.24)
    orange = material('Rescue Orange', (0.95, 0.11, 0.018), 0.22, 0.24, (0.95, 0.025, 0.003), 5)
    dark = material('Graphite', (0.008, 0.012, 0.018), 0.78, 0.17)
    glass = material('Marine Glass', (0.008, 0.16, 0.25), 0.12, 0.08)
    cyan = material('Telemetry Cyan', (0.01, 0.55, 0.95), 0.20, 0.16, (0.01, 0.35, 1.0), 6)
    rubber = material('Rubber', (0.012, 0.018, 0.022), 0.02, 0.65)
    yellow = material('Safety Yellow', (0.95, 0.60, 0.03), 0.08, 0.30)
    foam = material('Sea Foam', (0.60, 0.80, 0.84), 0.0, 0.28)
    water = setup_water()

    mats = (navy, white, orange, dark, glass, cyan, rubber, yellow)

    print('Creating ocean...')
    ocean = make_ocean(water)

    print('Creating vessel root...')
    root = bpy.data.objects.new('NAVRAKHSHAK_VESSEL', None)
    bpy.context.collection.objects.link(root)

    print('Creating realistic hull...')
    make_hull(root, white, navy, orange)

    print('Creating deck systems...')
    make_deck_equipment(root, mats)

    print('Creating bridge and superstructure...')
    make_superstructure(root, mats)

    print('Creating recovery crane...')
    make_crane(root, dark, orange)

    print('Creating water interaction...')
    make_ocean_foam(root, foam)
    make_wake(root, -1, foam)
    make_wake(root, 1, foam)

    print('Creating tactical environment...')
    add_geofence(cyan)

    print('Creating cinematic camera...')
    add_camera()

    print('Creating sky and lighting...')
    setup_world()
    add_lighting()

    # Vessel motion for the Blender preview.
    root.location = (0, 0, 0)
    root.keyframe_insert(data_path='location', frame=1)
    root.location = (8, 2, 0.18)
    root.keyframe_insert(data_path='location', frame=240)

    # Gentle roll/pitch to sell water movement.
    root.rotation_euler = (0, 0, 0)
    root.keyframe_insert(data_path='rotation_euler', frame=1)
    root.rotation_euler = (math.radians(1.4), math.radians(-0.8), math.radians(1.2))
    root.keyframe_insert(data_path='rotation_euler', frame=70)
    root.rotation_euler = (math.radians(-1.0), math.radians(0.9), math.radians(-1.0))
    root.keyframe_insert(data_path='rotation_euler', frame=140)
    root.rotation_euler = (0, 0, 0)
    root.keyframe_insert(data_path='rotation_euler', frame=240)

    # Render settings — Blender 5.2 uses BLENDER_EEVEE.
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = 240
    try:
        scene.render.engine = 'BLENDER_EEVEE'
    except Exception:
        try:
            scene.render.engine = 'BLENDER_EEVEE_NEXT'
        except Exception:
            scene.render.engine = 'CYCLES'

    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 65
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = PREVIEW_OUT
    scene.render.film_transparent = False
    safe_set(scene.view_settings, 'look', 'AgX - Medium High Contrast')
    scene.frame_set(70)

    # --------------------------------------------------------
    # Vessel-only export. No ocean, camera, lights or geofence.
    # --------------------------------------------------------
    bpy.ops.object.select_all(action='DESELECT')
    root.select_set(True)
    for child in root.children_recursive:
        child.select_set(True)
    bpy.context.view_layer.objects.active = root

    print('Exporting vessel-only GLB...')
    export_ok = False
    try:
        bpy.ops.export_scene.gltf(
            filepath=OUT,
            export_format='GLB',
            export_apply=True,
            use_selection=True,
            export_cameras=False,
            export_lights=False
        )
        export_ok = True
    except Exception as exc:
        print('GLB EXPORT ERROR:', repr(exc))

    print('Saving Blender scene...')
    blend_ok = False
    try:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
        blend_ok = True
    except Exception as exc:
        print('BLEND SAVE ERROR:', repr(exc))

    print('Rendering preview...')
    render_ok = False
    try:
        bpy.ops.render.render(write_still=True)
        render_ok = True
    except Exception as exc:
        print('PREVIEW RENDER ERROR:', repr(exc))

    print('')
    print('============================================================')
    print(' NAVRAKSHAK V2.1 BUILD COMPLETE')
    print('============================================================')
    print('GLB:', OUT)
    print('GLB SUCCESS:', export_ok)
    print('BLEND:', BLEND_OUT)
    print('BLEND SUCCESS:', blend_ok)
    print('PREVIEW:', PREVIEW_OUT)
    print('PREVIEW SUCCESS:', render_ok)
    print('ENGINE:', scene.render.engine)
    print('VESSEL ROOT:', root.name)
    print('OCEAN:', ocean.name)
    print('============================================================')


build()
