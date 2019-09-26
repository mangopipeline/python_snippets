'''
ckdtree example
'''
from time import time
import pymxs
MXS = pymxs.runtime
from scipy import spatial

def construct_kdtree(mesh):
	st = time()
	ws_mesh = MXS.snapshotAsMesh(mesh)
	verts = [[ws_mesh.verts[i].pos.x,ws_mesh.verts[i].pos.y, ws_mesh.verts[i].pos.z] for i in xrange(ws_mesh.verts.count)] 
	print "kdtree took %s seconds to build" % (time()-st)
	return spatial.cKDTree(verts)


def find_verts_by_distance_to_pos(pos,tree,radius):
	matches =  tree.query_ball_point(pos,radius)
	return [id+1 for id in matches]


#maxscript helper
MXS.execute('fn select_verts obj verts = obj.selectedVerts = verts')
	
if __name__ == '__main__':
	st = time()
	hlp = MXS.getNodeByName("Point001")
	msh = MXS.getNodeByName("Sphere001")

	kdtree = construct_kdtree(msh)
	verts = find_verts_by_distance_to_pos(hlp.pos,kdtree,25.0)
	print 'selecting verts %s' % verts
	MXS.select_verts(msh,verts)
	#msh.selectedVerts = verts
	print "total time %s seconds " % (time()-st)