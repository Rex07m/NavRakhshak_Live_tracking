import bpy, math, os
from mathutils import Vector

# NavRakhshak cinematic Blender builder — Blender 5.2 LTS.
# Builds a recognizable rescue/work boat, real horizontal ocean waves,
# procedural sky + sun, cinematic lighting, and a web-ready vessel GLB.

OUT_DIR = os.path.join(os.path.expanduser('~'), 'Downloads', 'NavRakhshak_Blender')
os.makedirs(OUT_DIR, exist_ok=True)
OUT = os.path.join(OUT_DIR, 'navrakshak_vessel.glb')
BLEND_OUT = os.path.join(OUT_DIR, 'navrakshak_cinematic.blend')
PREVIEW_OUT = os.path.join(OUT_DIR, 'navrakshak_preview.png')

# Avoid Windows file-lock collisions.
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


def mat(name, color, metallic=0.0, rough=.4, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = (*color, 1)
    bs = m.node_tree.nodes.get('Principled BSDF')
    if bs:
        if 'Base Color' in bs.inputs: bs.inputs['Base Color'].default_value = (*color, 1)
        if 'Metallic' in bs.inputs: bs.inputs['Metallic'].default_value = metallic
        if 'Roughness' in bs.inputs: bs.inputs['Roughness'].default_value = rough
        if emission and 'Emission Color' in bs.inputs:
            bs.inputs['Emission Color'].default_value = (*emission, 1)
            bs.inputs['Emission Strength'].default_value = 5.0
    return m


def water_material():
    m = mat('Ocean Water', (.008, .07, .13), .55, .16)
    nt = m.node_tree
    bs = nt.nodes.get('Principled BSDF')
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = .22
    noise.inputs['Detail'].default_value = 6.0
    noise.inputs['Roughness'].default_value = .72
    noise.inputs['Distortion'].default_value = .18
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .32
    bump.inputs['Distance'].default_value = .18
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (.004, .025, .05, 1)
    ramp.color_ramp.elements[1].color = (.015, .22, .34, 1)
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bs.inputs['Base Color'])
    bs.inputs['Metallic'].default_value = .35
    bs.inputs['Roughness'].default_value = .14
    if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value = .28
    if 'Coat Roughness' in bs.inputs: bs.inputs['Coat Roughness'].default_value = .08
    return m


def cube(name, loc, scale, material, bevel=.08, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
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
    # Cross-sections along X: pointed bow/stern, sloped sides, raised sheer.
    stations = [
        (-5.1,.08,-.18,.10), (-4.55,1.02,-.42,.28), (-3.2,1.38,-.58,.42),
        (-1.0,1.48,-.64,.50), (1.5,1.42,-.60,.48), (3.7,1.20,-.46,.38),
        (4.8,.62,-.25,.24), (5.15,.08,-.05,.10)
    ]
    verts=[]; faces=[]
    for x,w,bottom,deck in stations:
        verts += [(x,0,bottom),(x,w,bottom+.12),(x,w*.92,deck),(x,-w*.92,deck),(x,-w,bottom+.12)]
    for i in range(len(stations)-1):
        a=i*5; n=(i+1)*5
        for j in range(5):
            k=(j+1)%5; faces.append((a+j,n+j,n+k,a+k))
    faces += [(0,1,2,3,4),(35,39,38,37,36)]
    me=bpy.data.meshes.new(name+' Mesh'); me.from_pydata(verts, [], faces); me.update()
    o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(material); o.parent=parent
    bev=o.modifiers.new('Hull Edge Softening','BEVEL'); bev.width=.10; bev.segments=3
    for p in me.polygons: p.use_smooth=True
    return o


def make_ocean():
    # IMPORTANT: Blender Z is vertical. The previous version accidentally put
    # the wave height on Y, making the ocean effectively vertical.
    size=170; n=110
    verts=[]; faces=[]
    for j in range(n+1):
        y=(j/n-.5)*size
        for i in range(n+1):
            x=(i/n-.5)*size
            z=-1.18 + .22*math.sin(x*.13+y*.09) + .12*math.sin(x*.31-y*.21) + .055*math.cos((x+y)*.58)
            verts.append((x,y,z))
    for j in range(n):
        for i in range(n):
            a=j*(n+1)+i; b=a+1; c=a+n+2; d=a+n+1
            faces.append((a,b,c,d))
    me=bpy.data.meshes.new('Cinematic Ocean Mesh'); me.from_pydata(verts,[],faces); me.update()
    o=bpy.data.objects.new('Ocean',me); bpy.context.collection.objects.link(o); o.data.materials.append(WATER)
    for p in me.polygons: p.use_smooth=True
    # Animated shape key for visible swell motion in the Blender scene.
    basis=o.shape_key_add(name='Basis'); wave=o.shape_key_add(name='Wave_Swell')
    for v in wave.data:
        x,y=v.co.x,v.co.y
        v.co.z += .16*math.sin(x*.18+y*.12)
    key=o.data.shape_keys.key_blocks['Wave_Swell']
    for frame,val in [(1,0),(35,1),(70,0),(105,-.65),(140,0)]:
        key.value=val; key.keyframe_insert('value',frame=frame)
    if o.data.shape_keys.animation_data:
        for fc in o.data.shape_keys.animation_data.action.fcurves:
            for kp in fc.keyframe_points: kp.interpolation='SINE'
    return o


def wake(parent, side, material):
    cu=bpy.data.curves.new('Wake Curve','CURVE'); cu.dimensions='3D'; cu.bevel_depth=.10; cu.bevel_resolution=5
    sp=cu.splines.new('BEZIER'); sp.bezier_points.add(3)
    pts=[(4.0,side*.65,-.78),(7.0,side*1.05,-.88),(10.5,side*1.75,-.98),(14.0,side*2.35,-1.04)]
    for bp,co in zip(sp.bezier_points,pts): bp.co=co; bp.handle_left_type='AUTO'; bp.handle_right_type='AUTO'
    o=bpy.data.objects.new('Wake Foam',cu); bpy.context.collection.objects.link(o); cu.materials.append(material); o.parent=parent
    return o


# ---------- reset ----------
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)

navy=mat('Nav Navy',(.012,.075,.15),.72,.20)
white=mat('Hull White',(.72,.82,.86),.35,.22)
orange=mat('Rescue Orange',(.95,.16,.025),.28,.22,(.9,.04,.005))
dark=mat('Graphite',(.008,.018,.028),.82,.16)
glass=mat('Marine Glass',(.025,.27,.42),.18,.07)
cyan=mat('Telemetry Cyan',(.02,.72,1),.30,.14,(.02,.45,1))
rubber=mat('Rubber Fender',(.025,.035,.042),.05,.62)
foam=mat('Sea Foam',(.62,.82,.86),0,.28)
WATER=water_material()

# ---------- ocean ----------
make_ocean()
for r in (9,16,24,34,45): ring('Range Ring',r,-1.03,cyan)

# ---------- vessel ----------
root=bpy.data.objects.new('NAVRAKHSHAK_VESSEL',None); bpy.context.collection.objects.link(root)
make_hull('Hydrodynamic Hull',root,white)
cube('Safety Belt',(0,-1.42,.20),(4.2,.045,.10),orange,.025,root)
cube('Keel Line',(0,0,-.56),(3.6,.10,.055),dark,.02,root)
cube('Deck',(0,0,.55),(4.05,1.22,.12),dark,.10,root)
cube('Fore Deck',(-3.25,0,.62),(1.25,1.05,.10),white,.08,root)
cube('Aft Deck',(2.7,0,.64),(1.45,1.08,.10),dark,.08,root)
cube('Wheelhouse',(-.85,0,1.55),(1.55,1.02,.78),navy,.16,root)
cube('Front Windshield',(-2.43,0,1.82),(.035,.82,.48),glass,.025,root)
cube('Port Window',(-.82,1.035,1.78),(.72,.035,.38),glass,.025,root)
cube('Starboard Window',(-.82,-1.035,1.78),(.72,.035,.38),glass,.025,root)
cube('Wheelhouse Roof',(-.85,0,2.42),(1.78,1.15,.12),orange,.06,root)
for y in (-1.12,1.12):
    for x in (-3.55,-2.4,2.1,3.55): cyl('Deck Rail',(x,y,1.0),.025,.72,white,12,root)
    cube('Rail Top',(0,y,1.35),(3.65,.025,.025),white,.01,root)
cube('Aft Equipment',(2.5,0,1.18),(1.15,.82,.40),navy,.10,root)
mast=cyl('Radar Mast',(-.65,0,4.15),.085,3.1,white,18,root)
cyl('Antenna',(-.65,0,6.05),.035,1.15,orange,12,root)
cube('Radar Boom',(-.65,0,5.35),(1.35,.045,.045),dark,.01,root)
bpy.ops.mesh.primitive_torus_add(major_radius=.62,minor_radius=.07,major_segments=48,location=(-.65,0,5.95))
radar=bpy.context.object; radar.name='Radar Dish'; radar.data.materials.append(cyan); radar.parent=root
cyl('Emergency Beacon',(-.65,0,6.62),.16,.25,orange,24,root)
for x,c in [(-4.55,orange),(4.45,cyan)]: cyl('Nav Light',(x,0,.72),.09,.18,c,20,root)
for y in (-1.46,1.46): cube('Rubber Fender',(0,y,.18),(3.9,.07,.13),rubber,.04,root)
wake(root,-.72,foam); wake(root,.72,foam)

# ---------- tactical environment ----------
bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=18,depth=4,location=(0,0,1)); gf=bpy.context.object; gf.name='3D GEOFENCE'; gf.display_type='WIRE'; gf.data.materials.append(cyan)
ring('GEOFENCE INNER',18,3,cyan)
radar.rotation_euler=(0,0,0); radar.keyframe_insert('rotation_euler',frame=1,index=2); radar.rotation_euler.z=math.tau; radar.keyframe_insert('rotation_euler',frame=120,index=2)
root.location=(0,0,0); root.keyframe_insert('location',frame=1); root.location=(7,2,.15); root.keyframe_insert('location',frame=240)

# ---------- cinematic camera ----------
bpy.ops.object.camera_add(location=(24,-30,14)); cam=bpy.context.object; cam.name='Cinematic Camera'; bpy.context.scene.camera=cam; cam.data.lens=48
def look(obj,pt): obj.rotation_euler=(Vector(pt)-obj.location).to_track_quat('-Z','Y').to_euler()
look(cam,(0,0,.6)); cam.keyframe_insert('location',frame=1); cam.keyframe_insert('rotation_euler',frame=1)
cam.location=(17,-22,9); look(cam,(0,0,1.0)); cam.keyframe_insert('location',frame=80); cam.keyframe_insert('rotation_euler',frame=80)
cam.location=(-10,-17,7); look(cam,(1,0,1.0)); cam.keyframe_insert('location',frame=160); cam.keyframe_insert('rotation_euler',frame=160)
cam.location=(24,-30,14); look(cam,(0,0,.6)); cam.keyframe_insert('location',frame=240); cam.keyframe_insert('rotation_euler',frame=240)

# ---------- procedural sky + sun ----------
world=bpy.context.scene.world or bpy.data.worlds.new('NavRakhshak Sky'); bpy.context.scene.world=world; world.use_nodes=True
nt=world.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputWorld'); bg=nt.nodes.new('ShaderNodeBackground'); sky=nt.nodes.new('ShaderNodeTexSky')
try: sky.sky_type='MULTIPLE_SCATTERING'
except Exception:
    try: sky.sky_type='NISHITA'
    except Exception: pass
safe_set(sky,'sun_elevation',math.radians(18)); safe_set(sky,'sun_rotation',math.radians(145)); safe_set(sky,'sun_intensity',0.75); safe_set(sky,'sun_size',math.radians(.55)); safe_set(sky,'turbidity',3.2); safe_set(sky,'ground_albedo',.18)
bg.inputs['Strength'].default_value=.32; nt.links.new(sky.outputs['Color'],bg.inputs['Color']); nt.links.new(bg.outputs['Background'],out.inputs['Surface'])

bpy.ops.object.light_add(type='SUN',location=(-18,-18,25)); sun=bpy.context.object; sun.name='Maritime Sun'; sun.data.energy=4.2; sun.data.angle=math.radians(3.0); sun.rotation_euler=(math.radians(32),math.radians(-22),math.radians(-35))
bpy.ops.object.light_add(type='AREA',location=(-12,-14,18)); key=bpy.context.object; key.name='Warm Key'; key.data.energy=1500; key.data.shape='DISK'; key.data.size=14; key.data.color=(1.0,.48,.25)
bpy.ops.object.light_add(type='AREA',location=(12,8,12)); fill=bpy.context.object; fill.name='Ocean Fill'; fill.data.energy=1100; fill.data.size=12; fill.data.color=(.08,.42,1.0)
# Visible sun disc positioned inside the camera composition.
sunmat=mat('Sun Disc',(1.0,.20,.035),0,.2,(1.0,.08,.01))
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=3.2, location=(-17,-25,19)); disc=bpy.context.object; disc.name='Cinematic Sun Disc'; disc.data.materials.append(sunmat)

# ---------- render ----------
sc=bpy.context.scene
sc.frame_start=1; sc.frame_end=240
# Blender 5.2 LTS exposes EEVEE as BLENDER_EEVEE. Keep a fallback for other 5.x builds.
try:
    sc.render.engine='BLENDER_EEVEE'
except Exception:
    try: sc.render.engine='BLENDER_EEVEE_NEXT'
    except Exception: sc.render.engine='CYCLES'
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=70
sc.render.image_settings.file_format='PNG'; sc.render.filepath=PREVIEW_OUT
safe_set(sc.view_settings,'look','AgX - Medium High Contrast')
sc.render.film_transparent=False

# Export ONLY vessel hierarchy for the website. Ocean/sun stay in the Blender cinematic scene.
bpy.ops.object.select_all(action='DESELECT'); root.select_set(True)
for child in root.children_recursive: child.select_set(True)
bpy.context.view_layer.objects.active=root
bpy.ops.export_scene.gltf(filepath=OUT,export_format='GLB',export_apply=True,use_selection=True,export_cameras=False,export_lights=False)
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT)
# Render after all scene setup succeeds.
bpy.context.scene.frame_set(70)
bpy.ops.render.render(write_still=True)

print('NAVRAKSHAK CINEMATIC BUILD COMPLETE')
print('GLB:',OUT)
print('BLEND:',BLEND_OUT)
print('PREVIEW:',PREVIEW_OUT)
print('ENGINE:',sc.render.engine)
