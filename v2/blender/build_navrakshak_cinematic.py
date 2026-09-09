import bpy, math
from mathutils import Vector

# NavRakhshak local Blender builder — Blender 5.2.1 compatible.
# Builds a cinematic maritime vessel scene and exports a web-ready GLB.

OUT = bpy.path.abspath('//navrakshak_vessel.glb')


def mat(name, color, metallic=0.0, rough=.4, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*color, 1)
    bs.inputs['Metallic'].default_value = metallic
    bs.inputs['Roughness'].default_value = rough
    if emission:
        bs.inputs['Emission Color'].default_value = (*emission, 1)
        bs.inputs['Emission Strength'].default_value = 6
    return m


def cube(name, loc, scale, material, bevel=.08):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('Soft edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    o.data.materials.append(material)
    return o


def cyl(name, loc, radius, depth, material, verts=48):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    return o


def ring(name, radius, z, material):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=.035, major_segments=96, location=(0, 0, z))
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    return o


def wake_curve(name, y, material):
    # Direct curve-data construction for Blender 5.2 compatibility.
    cu_data = bpy.data.curves.new(name, 'CURVE')
    cu_data.dimensions = '3D'
    cu_data.bevel_depth = .09
    cu_data.bevel_resolution = 4
    spline = cu_data.splines.new('BEZIER')
    spline.bezier_points.add(3)
    pts = [(5, y, -.82), (7, y * 1.15, -.82), (10, y * .55, -.82), (13, 0, -.82)]
    for bp, co in zip(spline.bezier_points, pts):
        bp.co = co
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, cu_data)
    bpy.context.collection.objects.link(obj)
    cu_data.materials.append(material)
    return obj


# Clear scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

navy = mat('Nav Navy', (0.015, .08, .16), .65, .22)
white = mat('Hull', (0.72, .82, .86), .35, .24)
orange = mat('Rescue Orange', (.95, .19, .035), .25, .25, (.95, .08, .015))
dark = mat('Graphite', (.015, .025, .035), .8, .18)
glass = mat('Marine Glass', (.03, .32, .48), .25, .08)
cyan = mat('Telemetry Cyan', (.05, .75, 1), .35, .15, (.05, .55, 1))
water = mat('Ocean', (.008, .055, .095), .15, .2)

# Ocean and range rings
cube('Ocean', (0, 0, -1.2), (55, 55, .08), water, 0)
for r in (9, 16, 24, 34, 45):
    ring('Range Ring', r, -1.05, cyan)

# Vessel
root = bpy.data.objects.new('NAVRAKHSHAK_VESSEL', None)
bpy.context.collection.objects.link(root)

hull = cube('Hull', (0, 0, 0), (4.8, 1.35, .48), white, .28)
hull.parent = root
stripe = cube('Safety Stripe', (0, -1.37, .18), (4.5, .06, .12), orange, .03)
stripe.parent = root
base = cube('Deck', (0, 0, .62), (4.2, 1.25, .14), dark, .08)
base.parent = root
cabin = cube('Wheelhouse', (-.9, 0, 1.65), (1.65, 1.05, .85), navy, .12)
cabin.parent = root
wind = cube('Windshield', (-.92, -1.07, 1.92), (1.35, .05, .45), glass, .03)
wind.parent = root
roof = cube('Rescue Roof', (-.9, 0, 2.58), (1.9, 1.18, .12), orange, .05)
roof.parent = root
rear = cube('Aft Equipment', (2.2, 0, 1.12), (1.35, 1.0, .42), navy, .08)
rear.parent = root
mast = cyl('Radar Mast', (-.8, 0, 4.2), .09, 3.0, white, 16)
mast.parent = root
antenna = cyl('Antenna', (-.8, 0, 6.05), .035, 1.0, orange, 12)
antenna.parent = root

bpy.ops.mesh.primitive_cube_add(location=(-.8, 0, 5.35), scale=(1.45, .045, .045))
boom = bpy.context.object
boom.name = 'Radar Boom'
boom.data.materials.append(dark)
boom.parent = root

bpy.ops.mesh.primitive_torus_add(major_radius=.65, minor_radius=.055, major_segments=48, location=(-.8, 0, 5.95))
radar = bpy.context.object
radar.name = 'Radar Dish'
radar.data.materials.append(cyan)
radar.parent = root

be = cyl('Emergency Beacon', (-.8, 0, 6.55), .16, .25, orange, 24)
be.parent = root

for x, c in [(-3.9, orange), (3.9, cyan)]:
    l = cyl('Nav Light', (x, 0, .65), .09, .18, c, 20)
    l.parent = root

# Wake
for y in (-.8, .8):
    w = wake_curve('Wake', y, cyan)
    w.parent = root

# Geofence volume
bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=18, depth=4, location=(0, 0, 1))
gf = bpy.context.object
gf.name = '3D GEOFENCE'
gf.display_type = 'WIRE'
gf.data.materials.append(cyan)
ring('GEOFENCE INNER', 18, 3, cyan)

# Radar animation — intentionally avoids Blender 5.2 Action.fcurves API.
radar.rotation_euler = (0, 0, 0)
radar.keyframe_insert('rotation_euler', frame=1, index=2)
radar.rotation_euler.z = math.tau
radar.keyframe_insert('rotation_euler', frame=120, index=2)
radar.rotation_euler.z = math.tau * 2
radar.keyframe_insert('rotation_euler', frame=240, index=2)

# Vessel motion
root.location = (0, 0, 0)
root.keyframe_insert('location', frame=1)
root.location = (7, 2, .15)
root.keyframe_insert('location', frame=240)

# Cinematic camera
bpy.ops.object.camera_add(location=(25, -27, 18))
cam = bpy.context.object
cam.name = 'Cinematic Camera'
bpy.context.scene.camera = cam


def look(obj, pt):
    obj.rotation_euler = (Vector(pt) - obj.location).to_track_quat('-Z', 'Y').to_euler()


look(cam, (0, 0, 1.5))
cam.keyframe_insert('location', frame=1)
cam.keyframe_insert('rotation_euler', frame=1)
cam.location = (18, 28, 11)
look(cam, (3, 0, 1.3))
cam.keyframe_insert('location', frame=180)
cam.keyframe_insert('rotation_euler', frame=180)

# Lighting / world
world = bpy.context.scene.world or bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (.004, .012, .025, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = .22

bpy.ops.object.light_add(type='AREA', location=(-12, -14, 20))
bpy.context.object.data.energy = 1800
bpy.context.object.data.shape = 'DISK'
bpy.context.object.data.size = 14

bpy.ops.object.light_add(type='AREA', location=(14, 10, 8))
bpy.context.object.data.energy = 1100
bpy.context.object.data.color = (.1, .5, 1)
bpy.context.object.data.size = 10

# Render settings
sc = bpy.context.scene
sc.frame_start = 1
sc.frame_end = 240
sc.render.engine = 'BLENDER_EEVEE_NEXT'
sc.render.resolution_x = 1280
sc.render.resolution_y = 720
sc.render.resolution_percentage = 60
sc.render.filepath = bpy.path.abspath('//navrakshak_preview.png')

# Export GLB and save the source scene.
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath('//navrakshak_cinematic.blend'))
bpy.ops.render.render(write_still=True)

print('NAVRAKSHAK BUILD COMPLETE:', OUT)
