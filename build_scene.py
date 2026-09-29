import bpy, math, random, os
from mathutils import Vector
from math import sin, cos, pi, exp, sqrt
random.seed(19)
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color,metal=0,rough=.5):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
sand=mat('Earth • burnt umber',(.19,.115,.057),0,.92)
stone=mat('Plinth • ochre limestone',(.29,.19,.095),0,.8)
gold=mat('Watch • aged gold',(.52,.30,.095),.78,.29)
blue=mat('Enamel • faded blue',(.29,.50,.59),.12,.36)
ivory=mat('Enamel • parchment',(.77,.71,.52),.05,.45)
flesh=mat('Dream • wax ivory',(.64,.51,.34),0,.5)
dark=mat('Hands and eyelashes',(.025,.016,.01),.15,.45)
bark=mat('Dead olive wood',(.16,.09,.038),0,.95)
antmat=mat('Ant • obsidian',(.018,.012,.007),.25,.3)
copper=mat('Closed watch • copper',(.46,.18,.07),.65,.34)
water=mat('Sea • muted teal',(.105,.27,.31),.35,.23)
cliff=mat('Cliffs • golden sandstone',(.57,.36,.14),0,.9)
def mesh(name,verts,faces,material):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(material)
 for p in me.polygons:p.use_smooth=True
 return o
def uv(name,loc,scale,material):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(material)
 for p in o.data.polygons:p.use_smooth=True
 return o
def cube(name,loc,scale,material,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material)
 if bevel:m=o.modifiers.new('Worn edges','BEVEL');m.width=bevel;m.segments=3;o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
def tube(name,pts,r,material,radii=None):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=r;cu.bevel_resolution=3
 sp=cu.splines.new('POLY');sp.points.add(len(pts)-1)
 for i,p in enumerate(pts):sp.points[i].co=(*p,1);sp.points[i].radius=radii[i] if radii else 1
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(material);return o
def line(a,b,n=12):return [Vector(a).lerp(Vector(b),t/(n-1)) for t in range(n)]
cube('Endless dry plain',(0,-7,-.2),(38,36,.35),sand)
cube('Left geometric plinth',(-3,0,.96),(3.6,3,2),stone,.045)
cube('Still sea',(0,1010,-.13),(4000,2000,.15),water)
# Mineral surface relief, restrained enough to keep the dreamlike clarity.
for material,scale,strength in [(sand,9,.18),(stone,7,.13),(bark,5,.24),(cliff,4,.2),(flesh,18,.07)]:
 nt=material.node_tree;n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale;n.inputs['Detail'].default_value=3
 b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=strength;b.inputs['Distance'].default_value=.11;nt.links.new(n.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],nt.nodes.get('Principled BSDF').inputs['Normal'])
# Cliffs built from irregular stratified columns.
for i in range(19):
 x=4.5+i*.68;y=15+1.1*sin(i*.43);h=1.1+1.6*sin(pi*i/23)+random.uniform(-.3,.4)
 vs=[];N=7
 for level in range(4):
  for j in range(N):
   a=j*2*pi/N;rr=random.uniform(.75,1.08);vs.append((x+rr*cos(a),y+.8*rr*sin(a),-.05+h*level/3+random.uniform(-.15,.15)))
 fs=[tuple(range(N-1,-1,-1)),tuple(range(3*N,4*N))]
 for k in range(3):
  for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
 o=mesh('Coastal cliff %02d'%i,vs,fs,cliff)
 for p in o.data.polygons:p.use_smooth=False
# Dead tree tapered branching skeleton.
def branch(name,pts,r):tube(name,pts,r,bark,[max(.04,1-i/(len(pts)-.3)) for i in range(len(pts))])
branch('Olive • twisted trunk',[(-3.6,.65,1.96),(-3.65,.62,2.5),(-3.7,.7,3.2),(-3.55,.69,4),(-3.7,.8,4.8),(-3.62,.81,5.6)],.19)
branch('Olive • watch bearing limb',[(-3.6,.7,3.95),(-3.1,.72,4.22),(-2.4,.73,4.29),(-1.5,.73,4.24),(-.9,.75,4.32)],.12)
branch('Olive • split twig',[(-3.2,.72,4.18),(-2.91,.77,4.56),(-2.65,.78,4.83)],.075)
for j in range(5):
 a=j*2*pi/5;branch('Olive • exposed root',[(-3.6,.65,2.2),(-3.6+.35*cos(a),.65+.35*sin(a),2.03),(-3.6+.65*cos(a),.65+.65*sin(a),1.99)],.1)
# All watch components use the same nonlinear surface mapping.
def clock(name,mapper,face):
 nr=20;nt=96;vs=[mapper(0,0,0)]
 for k in range(1,nr+1):
  for j in range(nt):
   a=j*2*pi/nt;vs.append(mapper(k/nr*cos(a),k/nr*sin(a),0))
 fs=[]
 for j in range(nt):fs.append((0,1+j,1+(j+1)%nt))
 for k in range(nr-1):
  s=1+k*nt;t=s+nt
  for j in range(nt):fs.append((s+j,t+j,t+(j+1)%nt,s+(j+1)%nt))
 o=mesh(name+' • flexible enamel',vs,fs,face);m=o.modifiers.new('Enamel thickness','SOLIDIFY');m.thickness=.042
 tube(name+' • continuous gold bezel',[mapper(cos(j*2*pi/160),sin(j*2*pi/160),.022) for j in range(161)],.052,gold)
 for j in range(60):
  a=j*2*pi/60;r=.80 if j%5==0 else .87
  tube(name+' • dial mark %02d'%j,[mapper(r*cos(a),r*sin(a),.035),mapper(.93*cos(a),.93*sin(a),.035)],.012 if j%5==0 else .005,dark)
 for n,ang,length in [('hour',2.9,.46),('minute',1.22,.72)]:
  tube(name+' • '+n,[mapper(t*length*cos(ang),t*length*sin(ang),.058) for t in [i/20 for i in range(21)]],.021,dark)
 uv(name+' • pin',mapper(0,0,.07),(.055,.055,.055),gold)
 # Embossed Arabic numerals tangent to the warped dial.
 for number in range(1,13):
  a=pi/2-number*2*pi/12;u=.69*cos(a);v=.69*sin(a);p=Vector(mapper(u,v,.045));du=Vector(mapper(u+.001,v,.045))-p;dv=Vector(mapper(u,v+.001,.045))-p
  z=du.cross(dv).normalized();y=dv.normalized();x=y.cross(z).normalized()
  from mathutils import Matrix
  cu=bpy.data.curves.new(name+' numeral','FONT');cu.body=str(number);cu.align_x='CENTER';cu.align_y='CENTER';cu.size=.17;cu.extrude=.002
  ob=bpy.data.objects.new(name+' • '+str(number),cu);bpy.context.collection.objects.link(ob);ob.location=p;ob.rotation_euler=Matrix((x,y,z)).transposed().to_euler();cu.materials.append(dark)
def tablemap(u,v,d):
 # The front half spills over the plinth's front edge.
 q=-v;theta=max(0,(q-.05))*1.85
 if q<=.05:y=-1.34-q;z=2.045
 else:y=-1.39-.48*sin(theta);z=2.045-.98*(1-cos(theta))
 return (-2.43+u*.92,y,z+d)
clock('01 • Time spills over stone',tablemap,blue)
def treemap(u,v,d):
 q=(v+.3)*1.65
 return (-1.88+.65*u,.73-.40*cos(q)-d,3.45+.83*sin(q))
clock('02 • Time hangs from wood',treemap,ivory)
# A sculpted asymmetric dream head: longitudinal elliptical sections taper into a long nose.
vs=[];fs=[];N=96;M=70
for i in range(M+1):
 t=i/M;x=-.5+4.2*t
 width=.04+1.0*sin(pi*t)**.85*(1-.38*t)
 height=.06+.92*sin(pi*t)**1.3
 for j in range(N):
  a=2*pi*j/N;y=-.35+width*cos(a)+.2*sin(t*5);z=.13+height*(1+sin(a))*.62
  z+=.14*sin(3*pi*t)*sin(a)**2;vs.append((x,y,z))
for i in range(M):
 for j in range(N):fs.append((i*N+j,i*N+(j+1)%N,(i+1)*N+(j+1)%N,(i+1)*N+j))
fs.extend([tuple(range(N-1,-1,-1)),tuple(range(M*N,(M+1)*N))]);mesh('Sleeper • impossible waxen face',vs,fs,flesh)
uv('Sleeper • elongated nose',(.0,-.96,.30),(.63,.33,.23),flesh)
tube('Sleeper • closed eyelid',[(.15+i*.055,-1.07-.08*sin(i*pi/22),.55+.1*sin(i*pi/22)) for i in range(23)],.045,flesh)
for i in range(19):
 x=.24+i*.058;y=-1.09-.08*sin(i*pi/19);z=.55+.1*sin(i*pi/19)
 tube('Sleeper • eyelash %02d'%i,[(x,y,z),(x-.02,y-.15,z-.05),(x-.07,y-.28,z-.20)],.008,dark)
def facemap(u,v,d):
 x=1.6+.78*u;t=(x+.5)/4.2
 w=.04+sin(pi*t)**.85*(1-.38*t);h=.06+.92*sin(pi*t)**1.3
 a=v*1.62
 y=-.35+.2*sin(t*5)+w*sin(a)
 z=.13+h*(1+cos(a))*.62+.14*sin(3*pi*t)*cos(a)**2+.045+d
 return (x,y,z)
clock('03 • Time weighs on sleep',facemap,ivory)
# Closed copper watch and readable insect silhouettes.
uv('04 • closed copper pocket watch',(-3.75,-.89,2.09),(.58,.46,.105),copper)
tube('04 • copper rim',[(-3.75+.57*cos(j*2*pi/100),-.89+.45*sin(j*2*pi/100),2.1) for j in range(101)],.027,gold)
for k in range(24):
 x=-3.75+random.uniform(-.39,.39);y=-.89+random.uniform(-.29,.29);z=2.19;ang=random.random()*2*pi
 def pos(a,b,c=0):return (x+a*cos(ang)-b*sin(ang),y+a*sin(ang)+b*cos(ang),z+c)
 for a,s in [(-.049,.038),(0,.027),(.043,.031)]:uv('Ant %02d • body'%k,pos(a,0), (s,s*.7,s*.7),antmat)
 for j in range(3):
  for side in [-1,1]:tube('Ant %02d • leg'%k,[pos((j-1)*.025,0),pos((j-1)*.045,side*.05,.013),pos((j-1)*.061,side*.082,-.016)],.004,antmat)
for i in range(45):
 x=random.uniform(-8,9);y=random.uniform(-5,10)
 if -5<x<0 and -2<y<2:continue
 uv('Scattered weathered pebble',(x,y,.025),(random.uniform(.03,.12),random.uniform(.025,.09),random.uniform(.02,.06)),stone)
world=bpy.data.worlds.new('Dream dusk');bpy.context.scene.world=world;world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.31,.43,.57,1);world.node_tree.nodes['Background'].inputs[1].default_value=.38
bpy.ops.object.light_add(type='SUN',location=(-9,-8,12));sun=bpy.context.object;sun.name='Late sun • long shadows';sun.data.energy=3;sun.data.angle=.035;sun.rotation_euler=(math.radians(66),math.radians(-22),math.radians(-40));sun.data.color=(1,.77,.47)
bpy.ops.object.light_add(type='AREA',location=(0,-3,8));bpy.context.object.data.energy=420;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=9
bpy.ops.object.camera_add(location=(6,-19,8));cam=bpy.context.object;cam.name='Camera • painted perspective';target=Vector((-.4,2,1.6));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='PERSP';cam.data.lens=48;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='CYCLES';sc.cycles.samples=48;sc.cycles.use_denoising=True;sc.render.resolution_x=1400;sc.render.resolution_y=1050;sc.render.resolution_percentage=100
sc.view_settings.view_transform='AgX';sc.render.image_settings.file_format='PNG';sc.render.filepath=os.path.join(OUT,'persistence_of_memory.png')
# Save an immediately useful opening view.
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
sc['Artwork']='Surreal 3D study after Salvador Dali, The Persistence of Memory (1931)';sc['Source']='https://www.moma.org/collection/works/79018';sc['Notes']='Procedural geometry. Separate editable clocks, face, tree, ants and coastline. GLB uses base materials; Blender contains procedural bump shading.'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'persistence_of_memory.blend'))
# Convert curve lettering, branches and bezels for GLB without changing the saved editable blend.
bpy.ops.object.select_all(action='DESELECT')
for ob in list(sc.objects):
 if ob.type in {'CURVE','FONT'}:
  ob.select_set(True);bpy.context.view_layer.objects.active=ob;bpy.ops.object.convert(target='MESH');ob.select_set(False)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'persistence_of_memory.glb'),export_format='GLB',export_apply=True,export_cameras=True,export_lights=True)
bpy.ops.render.render(write_still=True)
print('DELIVERY_OK',len(sc.objects),'objects')
