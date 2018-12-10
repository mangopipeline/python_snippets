import pymxs
import MaxPlus
import time
MXS = pymxs.runtime
#defined some methods from MXS usually speeds things up (predeclaring)

get_face_normal = MXS.polyOp.getFaceNormal
get_num_faces = MXS.polyOp.getNumFaces
get_edges_using_face = MXS.polyOp.getEdgesUsingFace 
get_faces_using_edge = MXS.polyOp.getFacesUsingEdge
get_face_smooth_group = MXS.polyOp.getFaceSmoothGroup
get_face_area = MXS.polyOp.getFaceArea
get_verts_using_face = MXS.polyOp.GetVertsUsingFace

#this helps doing some magic conversion stuff :D
MaxPlus.Core.EvalMAXScript('fn __b2a b = (return b as Array)')
MaxPlus.Core.EvalMAXScript('fn __set_ba_val b i v =  b[i] = v')

def _bitarray_to_array(bitarray):
	return MXS.__b2a(bitarray)

def _bitarray_set_val(bitarray,index,val):
	MXS.__set_ba_val(bitarray,index,val)

def _angle_from_vectors(vec1,vec2):
	return MXS.acos(MXS.dot(vec1,vec2))

def _get_coplaner_faces(obj,face_id,coplanar_threshold,split_by_sg=False):
	crunch_faces = MXS.execute('#{%i}' % face_id)
	processed_faces = MXS.execute('#{%i}' % face_id)
	face_normal = get_face_normal(obj,face_id)
	face_sg = get_face_smooth_group(obj,face_id)
	
	while not crunch_faces.isEmpty:
		edges =  get_edges_using_face(obj,crunch_faces)
		faces = get_faces_using_edge(obj,edges) #TODO: mabye get from edges instead?
		crunch_faces = faces - processed_faces
		
		for face in _bitarray_to_array(crunch_faces):
			test_normal = get_face_normal(obj,face)
			angle = _angle_from_vectors(test_normal, face_normal)

			if angle  > coplanar_threshold:
				MXS.deleteitem(crunch_faces, face)
			
			elif (get_face_smooth_group(obj,face) & face_sg) is 0:
				MXS.deleteitem(crunch_faces, face)
			
		processed_faces = processed_faces + crunch_faces
		
		
	return processed_faces
	
def _get_face_weight(obj,faces):
	areas =[get_face_area(obj,face_id) for face_id in _bitarray_to_array(faces)]
	return sum(areas)
	

def _unify_normals(obj):
	mod = MXS.Edit_Normals()
	MXS.addModifier(obj,mod)
	normal_count = mod.GetNumNormals (node=obj)
	normal_sel = MXS.execute('#{1..%i}' % normal_count)
	mod.unify(selection=normal_sel)
	return mod
	

def apply_face_weighted_normals(obj, coplanear_threshold=0.1):
	if not MXS.canConvertTo(obj, MXS.editable_poly):
		raise ValueError('%s can not be converted to edit poly' % obj)
	
	MXS.convertTo(obj,MXS.editable_poly)
	
	nrm_mod = _unify_normals(obj)
	
	normal_count = nrm_mod.getNumNormals()
	
	normal_weights = [MXS.point3(0,0,0)] * normal_count
	
	for index in xrange(get_num_faces(obj)):
		face_id = index + 1
		face_normal = get_face_normal(obj, face_id)
		face_group = _get_coplaner_faces(obj,face_id,coplanear_threshold) 
		
		face_weight = _get_face_weight(obj,face_group)
		face_verts = get_verts_using_face(obj,face_id)

		for index in xrange(face_verts.count):
			normal_id = nrm_mod.getNormalID(face_id, index+1)
			if normal_id == 0:
				break
			
			index = normal_id -1 
			normal_weights[index] = normal_weights[index] +(face_normal * face_weight)
	
	# TODO: possibly add undo here at some point...
	for index,val in enumerate(normal_weights):
		normal_id = index+1
		nrm_mod.setNormalExplicit(normal_id, explicit=True)
		vec = MXS.normalize(val)
		nrm_mod.setNormal(normal_id,vec)
	
	MXS.subobjectlevel = 0
		
def apply_face_weigheted_surface_normals(objs=None, coplanear_threshold= 0.1):
	objs = objs or [obj for obj in MXS.selection]
	MXS.execute('max modify mode')
	start_time = time.time()
	
	if not objs:
		raise ValueError('nothing selected and no objects pass through')
	
	for obj in objs:
		apply_face_weighted_normals(obj, 
												coplanear_threshold=coplanear_threshold)
	
	print 'completed in  %s seconds' % (time.time()-start_time)
	
if __name__ == '__main__':
	import cProfile
	cProfile.run('apply_face_weigheted_surface_normals()')