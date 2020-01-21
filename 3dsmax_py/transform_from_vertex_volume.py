from __future__ import print_function

from numpy import matrix

from numpy.linalg import svd, norm
from pymxs import runtime as mxs
from scipy.spatial import ConvexHull


def volume_based_transform(obj):
    """
    creates a transform matrix by running a SVD operation on the verts that make up the mesh

    :param type obj: a max node...
    :returns: a transform matrix
    :rtype: mxs.matrix3
    """
    mesh = mxs.snapshotAsMesh(obj)  # let's work in world space :D
    print('collecting verts')
    verts = [[mesh.verts[i].pos.x, mesh.verts[i].pos.y, mesh.verts[i].pos.z] for i in range(mesh.verts.count)]

    print('making convexhull')
    hull = ConvexHull(verts)
    center = hull.points.mean(axis=0)

    print('centering points ch points')
    hull_verts = [hull.points[vert] - center for vert in hull.vertices]

    print('working out svd')
    pcloud = matrix(hull_verts)
    _, _, vh = svd(pcloud)

    print('building matrix')
    xaxis, yaxis, zaxis = vh.tolist()

    xaxis = mxs.point3(*map(float, xaxis))
    yaxis = mxs.point3(*map(float, yaxis))
    zaxis = mxs.point3(*map(float, zaxis))

    transform = mxs.matrix3(mxs.normalize(xaxis),
                            mxs.normalize(yaxis),
                            mxs.normalize(zaxis),
                            mxs.point3(*map(float, center)))

    return transform


if __name__ == '__main__':
    if not list(mxs.selection):
        raise RuntimeError('select something my guy')

    pnt = mxs.point(name='volume align transform')
    pnt.transform = volume_based_transform(mxs.selection[0])
    mxs.select(pnt)
