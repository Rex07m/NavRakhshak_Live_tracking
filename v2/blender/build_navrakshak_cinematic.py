import bpy, math, os
from mathutils import Vector

# NavRakhshak cinematic Blender builder — Blender 5.x.
# Creates a recognizable rescue/work boat, animated ocean, sun/sky environment,
# radar/geofence scene, cinematic camera, and a web-ready GLB.
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
        bs.inputs['Emission Strength'].default_value = 5.0
    return m


def cube(name, loc, scale, material, bevel=.08, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new('Soft edges', 'BEVEL'); mod.width = bevel; mod.segments = 3
    o.data.materials.append(material)
    if parent: o.parent = parent
    return o


def cyl(name, loc, radius, depth, material, verts=32, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth, location=loc)
    o = bpy.context.object; o.name = name; o.data.materials.append(material)
    if parent: o.parent = parent
    return o


def ring(name, radius, z, material, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=.035, major_segments=96, location=(0, 0, z))
    o = bpy.context.object; o.name = name; o.data.materials.append(material)
    if parent: o.parent = parent
    return o


def make_hull(name, parent, material):
    # Longitudinal loft: a tapered planform with a raised sheer line and pointed bow/stern.
    stations = [(-5.1,.08,-.18,.10),(-4.55,1.02,-.42,.28),(-3.2,1.38,-.58,.42),(-1.0,1.48,-.64,.50),(1.5,1.42,-.60,.48),(3.7,1.20,-.46,.38),(4.8,.62,-.25,.24),(5.15,.08,-.05,.10)]
    verts=[]
    # perimeter around each station: keel, lower port, upper port, upper starboard, lower starboard
    for x,w,bottom,deck in stations:
        verts += [(x,0,bottom),(x,w,bottom+.12),(x,w*.92,deck),(x,-w*.92,deck),(x,-w,bottom+.12)]
    faces=[]
    for i in range(len(stations)-1):
        a=i*5; n=(i+1)*5
        for j in range(5):
            k=(j+1)%5
            faces.append((a+j,n+j,n+k,a+k))
    # cap bow/stern
    faces += [(0,1,2,3,4),(35,39,38,37,36)]
    me=bpy.data.meshes.new(name+' Mesh'); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(material); o.parent=parent
    bev=o.modifiers.new('Hull Edge Softening','BEVEL'); bev.width=.10; bev.segments=3
    return o


def make_wave_ocean():
    size=150; n=90
    verts=[]; faces=[]
    for z in range(n+1):
        zz=(z/n-.5)*size
        for x in range(n+1):
            xx=(x/n-.5)*size
            y=-1.18 + .28*math.sin(xx*.22+zz*.17) + .13*math.sin(xx*.47-zz*.31) + .07*math.cos((xx+zz)*.62)
            verts.append((xx,zz,y))
    for z in range(n):
        for x in range(n):
            a=z*(n+1)+x; b=a+1; c=a+n+2; d=a+n+1
            faces.append((a,b,c,d))
    me=bpy.data.meshes.new('Cinematic Ocean Mesh'); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new('Ocean',me); bpy.context.collection.objects.link(o)
    o.data.materials.append(water)
    return o


# Clear scene
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
navy=mat('Nav Navy',(.012,.075,.15),.72,.20)
white=mat('Hull White',(.72,.82,.86),.35,.22)
orange=mat('Rescue Orange',(.95,.16,.025),.28,.22,(.9,.04,.005))
dark=mat('Graphite',(.008,.018,.028),.82,.16)
glass=mat('Marine Glass',(.025,.27,.42),.18,.07)
cyan=mat('Telemetry Cyan',(.02,.72,1),.3,.14,(.02,.45,1))
rubber=mat('Rubber Fender',(.025,.035,.042),.05,.62)
water=mat('Deep Ocean',(.006,.06,.105),.22,.12)
foam=mat('Sea Foam',(.55,.78,.82),.0,.32)

# Ocean and tactical rings
make_wave_ocean()
for r in (9,16,24,34,45): ring('Range Ring',r,-1.05,cyan)

# Vessel root: this is the node the web viewer extracts.
root=bpy.data.objects.new('NAVRAKHSHAK_VESSEL',None); bpy.context.collection.objects.link(root)
root.rotation_euler.z=0
make_hull('Hydrodynamic Hull',root,white)
# Orange safety belt and dark keel line.
cube('Safety Belt',(0,-1.42,.20),(4.2,.045,.10),orange,.025,root)
cube('Keel Line',(0,0,-.56),(3.6,.10,.055),dark,.02,root)
# Deck and raised fore/aft structures.
cube('Deck',(0,0,.55),(4.05,1.22,.12),dark,.10,root)
cube('Fore Deck',(-3.25,0,.62),(1.25,1.05,.10),white,.08,root)
cube('Aft Deck',(2.7,0,.64),(1.45,1.08,.10),dark,.08,root)
# Wheelhouse with sloped-looking roof layers.
cube('Wheelhouse',(-.85,0,1.55),(1.55,1.02,.78),navy,.16,root)
cube('Front Windshield',(-2.43,0,1.82),(.035,.82,.48),glass,.025,root)
cube('Port Window',(-.82,1.035,1.78),(.72,.035,.38),glass,.025,root)
cube('Starboard Window',(-.82,-1.035,1.78),(.72,.035,.38),glass,.025,root)
cube('Wheelhouse Roof',(-.85,0,2.42),(1.78,1.15,.12),orange,.06,root)
# Railings / rescue equipment.
for y in (-1.12,1.12):
    for x in (-3.55,-2.4,2.1,3.55): cyl('Deck Rail',(x,y,1.0),.025, .72,white,12,root)
    cube('Rail Top',(0,y,1.35),(3.65,.025,.025),white,.01,root)
cube('Aft Equipment',(2.5,0,1.18),(1.15,.82,.40),navy,.10,root)
# Radar mast, antenna, dish, beacon and navigation lights.
mast=cyl('Radar Mast',(-.65,0,4.15),.085,3.1,white,18,root)
cyl('Antenna',(-.65,0,6.05),.035,1.15,orange,12,root)
boom=cube('Radar Boom',(-.65,0,5.35),(1.35,.045,.045),dark,.01,root)
bpy.ops.mesh.primitive_torus_add(major_radius=.62,minor_radius=.07,major_segments=48,location=(-.65,0,5.95))
radar=bpy.context.object; radar.name='Radar Dish'; radar.data.materials.append(cyan); radar.parent=root
cyl('Emergency Beacon',(-.65,0,6.62),.16,.25,orange,24,root)
for x,c in [(-4.55,orange),(4.45,cyan)]: cyl('Nav Light',(x,0,.72),.09,.18,c,20,root)
# Fender strips.
for y in (-1.46,1.46): cube('Rubber Fender',(0,y,.18),(3.9,.07,.13),rubber,.04,root)
# Twin stylized wakes.
for y in (-.72,.72):
    cu=bpy.data.curves.new('Wake Curve','CURVE'); cu.dimensions='3D'; cu.bevel_depth=.10; cu.bevel_resolution=4
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(3)
    for bp,co in zip(sp.bezier_points,[(4.0,y,-.72),(7.0,y*1.15,-.78),(10.5,y*1.65,-.90),(14.0,y*2.0,-1.02)]): bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    w=bpy.data.objects.new('Wake',cu); bpy.context.collection.objects.link(w); cu.materials.append(foam); w.parent=root

# Geofence tactical volume.
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=18,depth=4,location=(0,0,1)); gf=bpy.context.object; gf.name='3D GEOFENCE'; gf.display_type='WIRE'; gf.data.materials.append(cyan)
ring('GEOFENCE INNER',18,3,cyan)
radar.rotation_euler=(0,0,0); radar.keyframe_insert('rotation_euler',frame=1,index=2); radar.rotation_euler.z=math.tau; radar.keyframe_insert('rotation_euler',frame=120,index=2); radar.rotation_euler.z=math.tau*2; radar.keyframe_insert('rotation_euler',frame=240,index=2)
root.location=(0,0,0); root.keyframe_insert('location',frame=1); root.location=(7,2,.15); root.keyframe_insert('location',frame=240)

# Cinematic camera.
bpy.ops.object.camera_add(location=(25,-27,18)); cam=bpy.context.object; cam.name='Cinematic Camera'; bpy.context.scene.camera=cam
def look(obj,pt): obj.rotation_euler=(Vector(pt)-obj.location).to_track_quat('-Z','Y').to_euler()
look(cam,(0,0,1.2)); cam.keyframe_insert('location',frame=1); cam.keyframe_insert('rotation_euler',frame=1)
cam.location=(18,28,11); look(cam,(3,0,1.0)); cam.keyframe_insert('location',frame=180); cam.keyframe_insert('rotation_euler',frame=180)

# Realistic sky + sun environment.
world=bpy.context.scene.world or bpy.data.worlds.new('World'); bpy.context.scene.world=world; world.use_nodes=True
wn=world.node_tree.nodes; bg=wn.get('Background'); bg.inputs['Color'].default_value=(.015,.055,.10,1); bg.inputs['Strength'].default_value=.30
bpy.ops.object.light_add(type='SUN',location=(-20,-20,25)); sun=bpy.context.object; sun.name='Maritime Sun'; sun.data.energy=4.0; sun.data.angle=math.radians(3); sun.rotation_euler=(math.radians(28),math.radians(-18),math.radians(-32))
bpy.ops.object.light_add(type='AREA',location=(-12,-14,20)); bpy.context.object.data.energy=1700; bpy.context.object.data.shape='DISK'; bpy.context.object.data.size=14
bpy.ops.object.light_add(type='AREA',location=(14,10,8)); fill=bpy.context.object; fill.data.energy=1000; fill.data.color=(.08,.42,1); fill.data.size=12
# Large emissive sun-disc for the preview render.
sunmat=mat('Sun Glow',(1.0,.24,.06),0,.25,(1.0,.12,.02)); bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=3.8,location=(-34,32,30)); sun_disc=bpy.context.object; sun_disc.name='Cinematic Sun'; sun_disc.data.materials.append(sunmat)

# Render settings.
sc=bpy.context.scene; sc.frame_start=1; sc.frame_end=240; sc.render.engine='BLENDER_EEVEE_NEXT'; sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=60; sc.render.filepath=PREVIEW_OUT
sc.view_settings.look='AgX - Medium High Contrast'
# Slight atmospheric depth without expensive volumetrics.
sc.render.film_transparent=False

# Export ONLY the vessel hierarchy so the website never scales the ocean/geofence with the boat.
bpy.ops.object.select_all(action='DESELECT'); root.select_set(True)
for child in root.children_recursive: child.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_apply=True,use_selection=True,export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
bpy.ops.render.render(write_still=True)
print('NAVRAKSHAK CINEMATIC BUILD COMPLETE:'); print('GLB:',OUT); print('BLEND:',BLEND_OUT); print('PREVIEW:',PREVIEW_OUT)
