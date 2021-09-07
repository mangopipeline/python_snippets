'''
Created on May 7, 2015

@author: carlos
'''

import os
from maya import cmds
from pymel.core.general import ls
import xml.etree.cElementTree as ET
import matrixHelpers as mh
reload(mh)

from xml.etree import ElementTree
from xml.dom import minidom
from math import tan
class mangoCamOps(object):    
    def prettify(self,elem):
        """
        Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    
    def camFrameDic(self,cam,t,ress):
        mat = cmds.getAttr('%s.worldMatrix' % cam,t=t)
        
        '''
        if cmds.upAxis( q=True, axis=True ) == 'y':
            mat = mh.listToMatrix(mat)
            mat = mh.objectWSMatrixZUpNP(mat)
            mat = mh.matrixToList(mat)
        '''
        
        pyCam = ls(cam)[0].getShape()
        fov = pyCam.getHorizontalFieldOfView()
        panx = pyCam.getHorizontalPan()
        pany = pyCam.getVerticalPan()
        aptx = pyCam.getHorizontalFilmAperture()  #inches 
        lens = aptx/(2.*tan(fov/2.))
        apty = aptx/(float(ress[1])/float(ress[0]))
        

        fDic = {'aperturex':str(aptx),
                'aperturey':str(apty),
                'distortion':"",
                'fov':str(fov),
                'frame':str(t),
                'lens':str(lens),
                'matrix':str(mat)[1:-1].replace(',',''),
                'panx':str(panx),
                'pany':str(pany)}
        
        return fDic
    
    def getFps(self):
        fps = cmds.currentUnit (q=True,t=True)
        if fps == 'game':return 15
        if fps == 'film':return 24
        if fps == 'pal':return 25 
        if fps == 'ntsc':return 30
        if fps == 'show':return 48 
        if fps == 'palf':return 50
        if fps == 'ntscf':return 60 
    
    def exportCamList(self,cams,fpn,startF,endF,preRoll=0):
        if not os.path.isdir(os.path.dirname(fpn)):raise ('camToXml:output directory does not exist')
        root = ET.Element("camera_export")
        rH = cmds.getAttr('defaultResolution.height')
        rW = cmds.getAttr('defaultResolution.width')
        dar = cmds.getAttr('defaultResolution.deviceAspectRatio')
        par = (float(rH)/float(rW))*dar
        fps = self.getFps()
        
        startF -= preRoll
        endF += preRoll
        
        dic = {'exportdate':'None',
               'exportfilename':'None',
               'firstframe':str(startF),
               'frame_rate':str(fps),
               'lastframe':str(endF),
               'pixelaspectratio':str(par),
               'resheight':str(rH),
               'reswidth':str(rW),
               'software':"maya",
               'sourcefilename':'None',
               'unitLinear':str(cmds.currentUnit(q=True,fullName=True)),
               'version':'None'}
        
        for k in dic:root.set(k,dic[k])
        camEL = []
        for c in cams:
            camE = ET.SubElement(root,'camera')
            camDic = {'centrecam':'',
                      'name':c,
                      'parent':'',
                      'position':'',
                      'type':''}
            
            for k in camDic:camE.set(k,camDic[k])
            camEL.append(camE)
            
        cmds.refresh(su=True)
        
        for t in xrange(startF,endF+1):
            cmds.setAttr("time1.outTime",t)
            for i in range(len(cams)):
                c = cams[i]
                se = camEL[i]
                fE = ET.SubElement(se,'frame')
                
                fDic = self.camFrameDic(c,t,(rH,rW))
                for k in fDic:fE.set(k,fDic[k])

        cmds.refresh(su=False)
        
        root = self.prettify(root)
        
        f = open(fpn,'w')
        f.writelines(root) 
        f.close()   
        
if __name__ == '__main__':
    c2x = mangoCamOps()
    c2x.exportCamList(['camera1'],r'c:\temp\mayaCam.xml',25,48)