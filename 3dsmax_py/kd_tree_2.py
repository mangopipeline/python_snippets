'''
ckdtree example
'''
from time import time
import pymxs
MXS = pymxs.runtime
from scipy import spatial
from pprint import pprint 

def extract_verts(mesh):
	'''
	this method maps point3 values to arrays so that scipy will be happy
	'''
	ws_mesh = MXS.snapshotAsMesh(mesh)
	return [[ws_mesh.verts[i].pos.x,ws_mesh.verts[i].pos.y,ws_mesh.verts[i].pos.z] for i in xrange(ws_mesh.verts.count)] 


def group_verts_by_distance(verts,radius):
	'''
	this method packs a verts list into a kdtree and then loops through each position to find any neighbors
	'''
	st = time()
	tree = spatial.cKDTree(verts)
	dic = {}
	
	for id,pos in enumerate(verts):
		dic[id] = tree.query_ball_point(pos,radius)
		
	print "data generated in %s seconds for %s verts" % (len(verts), time()-st)
	return dic

if __name__ == '__main__':
	st = time()
	#find the mesh by name
	msh = MXS.getNodeByName("Sphere001")
	#pull all the vert positions
	verts = extract_verts(msh)
	
	#create a dictionary where the key is the verted id and the value is a list of id for vertexes that are withing the given radius
	groups = group_verts_by_distance(verts,10.0)
	
	#print the id's for matches on th first vert
	print 'vert id %s matches are %s' % (0, groups[0])
	
