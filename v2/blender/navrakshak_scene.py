"""NavRakhshak local Blender scene builder.
Run inside Blender 5.x: Scripting > New > paste > Run Script.
Creates a cinematic maritime command scene, animates ocean/radar/beacon/camera,
and optionally exports a web-ready GLB beside the .blend file.
"""
import bpy, math
from mathutils import Vector
from math import sin, cos, pi

# ---------- reset ----------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
    pass
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 70
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 180
scene.render.image_settings.file_format = 'PNG'
scene.world.color = (0.003, 0.012, 0.022)

# ---------- materials ----------
def mat(name, color, metallic=0.0, rough=.35, emission=None, strength=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*emission,1); bs.inputs['Emission Strength'].default_value=strength
    return m
NAVY=mat('NavRakhshak Navy',(0.018,0.10,0.18),.65,.2, (0.01,0.05,0.09),.5)
WHITE=mat('Hull White',(.72,.82,.86),.45,.25)
ORANGE=mat('Safety Orange',(.95,.20,.055),.35,.22,(.45,.06,.01),.35)
DARK=mat('Graphite',(.015,.025,.032),.7,.16)
GLASS=mat('Marine Glass',(.03,.35,.52),.25,.08,(.01,.12,.18),.45)
WATER=mat('Deep Ocean',(.008,.08,.14),.35,.22)
CYAN=mat('Navigation Cyan',(.05,.75,1.0),.25,.15,(.02,.55,1),4)

# ---------- helpers ----------
def cube(name, loc, scale, material, bevel=.08):
    bpy.ops.mesh.primitive_cube_add(location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=o.modifiers.new('Edge Softening','BEVEL'); mod.width=bevel; mod.segments=3
    o.data.materials.append(material); return o

def cyl(name, loc, radius, depth, material, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=radius,depth=depth,location=loc); o=bpy.context.object; o.name=name; o.data.materials.append(material); return o

def torus(name, loc, major, minor, material):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=96,minor_segments=8,location=loc,rotation=(0,0,0)); o=bpy.context.object; o.name=name; o.data.materials.append(material); return o

# ---------- ocean ----------
bpy.ops.mesh.primitive_grid_add(x_subdivisions=100,y_subdivisions=100,size=180,location=(0,0,0))
ocean=bpy.context.object; ocean.name='OCEAN_DYNAMIC'; ocean.data.materials.append(WATER)
ocean.rotation_euler.x=0
for p in ocean.data.vertices:
    x,y=p.co.x,p.co.y
    p.co.z=0.10*sin(x*.10)+0.07*cos(y*.13)+0.04*sin((x+y)*.05)
for f in ocean.data.polygons: f.use_smooth=True
# shape keys for looping wave animation
basis=ocean.shape_key_add(name='Basis'); wave=ocean.shape_key_add(name='WavePeak')
for p in wave.data:
    x,y=p.co.x,p.co.y; p.co.z += .12*sin(x*.17+y*.11)
ocean.data.shape_keys.key_blocks['WavePeak'].value=0
ocean.data.shape_keys.key_blocks['WavePeak'].keyframe_insert('value',frame=1)
ocean.data.shape_keys.key_blocks['WavePeak'].value=1
ocean.data.shape_keys.key_blocks['WavePeak'].keyframe_insert('value',frame=45)
ocean.data.shape_keys.key_blocks['WavePeak'].value=0
ocean.data.shape_keys.key_blocks['WavePeak'].keyframe_insert('value',frame=90)
for fc in ocean.data.shape_keys.animation_data.action.fcurves: 
    for kp in fc.keyframe_points: kp.interpolation='SINE'

# ---------- vessel ----------
vessel=bpy.data.objects.new('NAVRAKSHAK_VESSEL',None); bpy.context.collection.objects.link(vessel)
hull=cube('Vessel_Hull',(0,0.55,1.0),(3.9,1.0,.55),WHITE,.18); hull.parent=vessel
stripe=cube('Safety_Stripe',(0,0.62,1.48),(3.55,1.03,.10),ORANGE,.04); stripe.parent=vessel
deck=cube('Main_Deck',(-.15,.58,1.72),(2.9,.9,.10),DARK,.05); deck.parent=vessel
cab=cube('Wheelhouse',(-.85,.58,2.55),(1.25,.75,.72),NAVY,.10); cab.parent=vessel
wind=cube('Front_Glass',(-1.15,-.20,2.75),(.65,.06,.28),GLASS,.03); wind.parent=vessel
roof=cube('Wheelhouse_Roof',(-.85,.58,3.34),(1.45,.88,.09),ORANGE,.04); roof.parent=vessel
aft=cube('Aft_Work_Deck',(1.55,.58,2.20),(1.25,.82,.30),NAVY,.08); aft.parent=vessel
mast=cyl('Radar_Mast',(-.65,.58,5.0),.06,3.0,WHITE,16); mast.parent=vessel
antenna=cyl('Antenna',(-.65,.58,6.9),.025,.9,ORANGE,12); antenna.parent=vessel
boom=cyl('Fishing_Boom',(.5,.58,4.35),.035,2.6,DARK,12); boom.rotation_euler.y=pi/2; boom.parent=vessel
beacon=cyl('Emergency_Beacon',(-.65,.58,7.38),.12,.16,ORANGE,24); beacon.parent=vessel
# running lights
for x,z,m in [(-3.7,1.75,ORANGE),(3.7,1.75,CYAN)]:
    lamp=cyl('Nav_Light', (x,.58,z), .10,.12,m,20); lamp.rotation_euler.x=pi/2; lamp.parent=vessel

# ---------- radar ----------
radar=bpy.data.objects.new('RADAR_SYSTEM',None); bpy.context.collection.objects.link(radar)
for i,r in enumerate((7,12,18,25)):
    q=torus(f'Radar_Ring_{i}',(0,0,.12),r,.035,CYAN if i==3 else ORANGE); q.parent=radar
bar=cube('Radar_Sweep',(0,0,1.0),(8.5,.06,.03),CYAN,.01); bar.parent=radar
# rotate around Z in top-down plane
radar.rotation_euler.z=0; radar.keyframe_insert('rotation_euler',frame=1,index=2); radar.rotation_euler.z=2*pi; radar.keyframe_insert('rotation_euler',frame=90,index=2)
for fc in radar.animation_data.action.fcurves:
    for kp in fc.keyframe_points: kp.interpolation='LINEAR'

# ---------- geofence ----------
geofence=bpy.data.objects.new('GEOFENCE_VOLUME',None); bpy.context.collection.objects.link(geofence)
for z in (-.1,5.0):
    q=torus('Geofence_Ring',(0,0,z),15,.045,CYAN); q.parent=geofence
cylg=cyl('Geofence_Cylinder',(0,0,2.45),15,4.9,CYAN,96); cylg.parent=geofence
cylg.display_type='WIRE'; cylg.hide_render=True

# ---------- wake ----------
for side in (-1,1):
    curve=bpy.data.curves.new('WakeCurve','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.10; curve.bevel_resolution=3
    spl=curve.splines.new('BEZIER'); spl.bezier_points.add(2)
    pts=[(3.0,side*.3,.28),(7.0,side*1.5,.22),(12.0,side*3.0,.18)]
    for bp,co in zip(spl.bezier_points,pts): bp.co=co; bp.handle_left_type=bp.handle_right_type='AUTO'
    obj=bpy.data.objects.new('Wake_Foam',curve); bpy.context.collection.objects.link(obj); obj.data.materials.append(WHITE); obj.parent=vessel

# ---------- lighting ----------
def light(name,typ,loc,energy,color,size=5):
    data=bpy.data.lights.new(name,typ); data.energy=energy; data.color=color; data.shadow_soft_size=size
    o=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(o); o.location=loc; return o
light('Key_Sun','SUN',(-20,-20,30),3.5,(1.0,.65,.45),5)
light('Ocean_Fill','AREA',(15,5,18),900,(.15,.55,1.0),12)
light('Orange_Rim','POINT',(-8,2,7),600,(1.0,.12,.03),3)

# ---------- camera ----------
bpy.ops.object.camera_add(location=(22,-25,15)); cam=bpy.context.object; cam.name='Cinematic_Delivery_Camera'; scene.camera=cam; cam.data.lens=48
def track(obj,pt): obj.rotation_euler=(Vector(pt)-obj.location).to_track_quat('-Z','Y').to_euler()
track(cam,(0,0,1.5)); cam.keyframe_insert('location',frame=1); cam.keyframe_insert('rotation_euler',frame=1)
cam.location=(15,-18,9); track(cam,(0,0,1.8)); cam.keyframe_insert('location',frame=60); cam.keyframe_insert('rotation_euler',frame=60)
cam.location=(-8,-14,6); track(cam,(0,0,2)); cam.keyframe_insert('location',frame=120); cam.keyframe_insert('rotation_euler',frame=120)
cam.location=(22,-25,15); track(cam,(0,0,1.5)); cam.keyframe_insert('location',frame=180); cam.keyframe_insert('rotation_euler',frame=180)

# vessel gentle motion loop
for f,z in [(1,.15),(45,.25),(90,.15),(135,.22),(180,.15)]:
    vessel.location.z=z; vessel.location.keyframe_insert('z',frame=f)
    vessel.rotation_euler.y=.02*sin(f*.05); vessel.rotation_euler.keyframe_insert('rotation_euler',frame=f)

# beacon pulse
for f,val in [(1,0.7),(15,1.4),(30,.7),(45,1.4),(60,.7)]:
    beacon.scale=(1,1,val); beacon.keyframe_insert('scale',frame=f)

# ---------- render look ----------
scene.view_settings.look='AgX - Medium High Contrast'
scene.render.film_transparent=False
# save beside current blend if possible
path=bpy.path.abspath('//NavRakhshak_Cinematic_3D.blend')
bpy.ops.wm.save_as_mainfile(filepath=path)
# web export
try:
    bpy.ops.export_scene.gltf(filepath=bpy.path.abspath('//NavRakhshak_Cinematic_3D.glb'),export_format='GLB',export_apply=True)
except Exception as exc:
    print('GLB export skipped:',exc)
# render preview
scene.render.filepath=bpy.path.abspath('//NavRakhshak_preview.png')
scene.frame_set(60)
bpy.ops.render.render(write_still=True)
print('NavRakhshak scene built:',path)
