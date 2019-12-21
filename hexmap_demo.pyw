import wx
import threading
import numpy as np
import math
import copy
from collections import OrderedDict
from hexmap import Iterators
from hexmap.Coords import Cube
from hexmap.Coords import Axial
from hexmap.Maps import RadialMap
def pixel_to_hex(point,zoom):
    q=((2./3)*point[0])/zoom
    r=(((-1./3)*point[0])+(np.sqrt(3)/3)*point[1])/zoom
    return round(Axial(q,r).toCube())
class Observable:
    def __init__(self, initialValue=None):
        self.data = initialValue
        self.callbacks = OrderedDict()
    def addCallback(self, func):
        self.callbacks[func] = 1
    def delCallback(self, func):
        del self.callbacks[func]
    def _docallbacks(self):
        for func in self.callbacks:
            func(self.data)
    def set(self, data):
        self.data = data
        self._docallbacks()
    def get(self):
        return self.data
    def unset(self):
        self.data = None
class RenderPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.offset_coord=(0,0)
        self.old_mouse_coord=(0,0)
        self.new_mouse_coord=(0,0)
        self.is_dragging=False
        self.is_left_click_down=False
        self.zoom=10
        self.selected_tile=Cube(0,0,0)
        self.hovered_tile=Cube(0,0,0)
        self.notation_type='None'
        self.pens={
            'x':wx.Pen('green'),
            'y':wx.Pen('pink'),
            'z':wx.Pen(wx.Colour(30,144,255)),
            'q':wx.Pen('green'),
            'r':wx.Pen('pink'),
            'hex_outline':wx.Pen('black')
        }
        self.brushes={
            'background':wx.Brush('white'),
            'not_passable_tile':wx.Brush(wx.Colour(0,0,0)),
            'movement_cost_1_tile':wx.Brush(wx.Colour(255,255,255)),
            'movement_cost_2_tile':wx.Brush(wx.Colour(139,69,19))
        }
        self.Show(True)
    def init(self,hexmap,lock):
        self.hexmap=hexmap
        self.lock=lock
        self.dc=Observable(wx.MemoryDC())
        self.dc.addCallback(self.Draw)
        self.OnSize(None)
        self.Draw(self.dc.get())
        self.Bind(wx.EVT_SIZE,self.OnSize)
        self.Bind(wx.EVT_PAINT,self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS,self.UpdateMouse)
    @property
    def hexagon(self):
        return [(((self.zoom)*np.cos((np.pi/180)*(60*i))),
                 ((self.zoom)*np.sin((np.pi/180)*(60*i)))) for i in range(0,6)]
    def OnPaint(self,event):
        wx.BufferedPaintDC(self,self.buffer)
    def OnSize(self,event):
        self.buffer=wx.Bitmap(*self.GetSize())
        self.UpdateDrawing()
    def Draw(self,dc):
        dc.SelectObject(self.buffer)
        dc.SetUserScale(self.zoom,self.zoom)
        dc.SetBackground(self.brushes['background'])
        dc.Clear()
        self.lock.acquire()
        for x,y,z in Iterators.RingIterator(self.hexmap.radius,6):
            height=self.zoom*np.sqrt(3)
            width=self.zoom*2
            center_x,center_y=(self.GetSize()/self.zoom)/2
            x_coord=x*((width/4)*3)
            y_coord=(y*(height/2))-(z*(height/2))
            h=[(vert[0]+x_coord+center_x+self.offset_coord[0],
                vert[1]-y_coord+center_y+self.offset_coord[1]) for vert in self.hexagon]
            tile=self.hexmap[Cube(x,y,z)]
            dc.SetBrush(wx.Brush(wx.Colour(255,255,255)))
            if (x,y,z)==(self.hovered_tile.x,self.hovered_tile.y,self.hovered_tile.z):
                dc.SetBrush(wx.Brush(wx.Colour(0,255,255)))
            elif (x,y,z)==(self.selected_tile.x,self.selected_tile.y,self.selected_tile.z):
                dc.SetBrush(wx.Brush(wx.Colour(0,0,255)))
            elif tile!=False:
                if tile.isPassable==False:
                    dc.SetBrush(self.brushes['not_passable_tile'])
                elif tile.movement_cost==1:
                    dc.SetBrush(self.brushes['movement_cost_1_tile'])
                elif tile.movement_cost==2:
                    dc.SetBrush(self.brushes['movement_cost_2_tile'])
            dc.SetPen(self.pens['hex_outline'])
            dc.DrawPolygon(h)
            if self.notation_type=='Cube':
                x_w,x_h=dc.GetTextExtent(str(x))
                x_x=x_coord+center_x+self.offset_coord[0]-(x_w/2)
                x_y=-y_coord+center_y+self.offset_coord[1]-(height/3)
                dc.SetPen(self.pens['x'])
                dc.DrawText(str(x),x_x,x_y)
                y_w,y_h=dc.GetTextExtent(str(y))
                y_x=x_coord+center_x+self.offset_coord[0]-(width/4)
                y_y=-y_coord+center_y+self.offset_coord[1]+(height/4)-y_h
                dc.SetPen(self.pens['y'])
                dc.DrawText(str(y),y_x,y_y)
                z_w,z_h=dc.GetTextExtent(str(z))
                z_x=x_coord+center_x+self.offset_coord[0]+(width/4)-z_w
                z_y=-y_coord+center_y+self.offset_coord[1]+(height/4)-z_h
                dc.SetPen(self.pens['z'])
                dc.DrawText(str(z),z_x,z_y)
            elif self.notation_type=='Axial':
                x_w,x_h=dc.GetTextExtent(str(y))
                x_x=x_coord+center_x+self.offset_coord[0]-(width/4)
                x_y=-y_coord+center_y+self.offset_coord[1]-(x_h/2)
                dc.DrawText(str(x),x_x,x_y)
                y_w,y_h=dc.GetTextExtent(str(z))
                y_x=x_coord+center_x+self.offset_coord[0]+(width/4)-y_w
                y_y=-y_coord+center_y+self.offset_coord[1]-(y_h/2)
                dc.DrawText(str(y),y_x,y_y)
            self.DrawAxis(dc)
        self.lock.release()
    def DrawAxis(self,dc):
        if self.notation_type=='Cube':
            width=((self.GetSize()[0]/16)/10)/2
            height=width*2
            xoffset=((self.GetSize()[0]/16)/10)
            yoffset=((self.GetSize()[1]/16)*15)/10
            x1=wx.Point(width*np.cos((np.pi/180)*180),height*np.sin((np.pi/180)*180))
            x2=wx.Point(width*np.cos((np.pi/180)*0),height*np.sin((np.pi/180)*0))
            dc.SetPen(self.pens['x'])
            dc.DrawLines([x1,x2],xoffset=xoffset,yoffset=yoffset)
            x1w,x1h=dc.GetTextExtent('-X')
            x1=wx.Point((width*np.cos((np.pi/180)*180))+xoffset,(height*np.sin((np.pi/180)*180))+yoffset-(x1h/2))
            dc.DrawText('-X',x1)
            x2w,x2h=dc.GetTextExtent('+X')
            x2=wx.Point((width*np.cos((np.pi/180)*0))+xoffset-(x2w/2),(height*np.sin((np.pi/180)*0))+yoffset-(x2h/2))
            dc.DrawText('+X',x2)
            y1=wx.Point(width*np.cos((np.pi/180)*210),height*np.sin((np.pi/180)*210))
            y2=wx.Point(width*np.cos((np.pi/180)*30),height*np.sin((np.pi/180)*30))
            dc.SetPen(self.pens['y'])
            dc.DrawLines([y1,y2],xoffset=xoffset,yoffset=yoffset)
            y1w,y1h=dc.GetTextExtent('-Y')
            y1=wx.Point((width*np.cos((np.pi/180)*30))+xoffset-y1w-(y1w/2),(height*np.sin((np.pi/180)*30))+yoffset-y1h)
            dc.DrawText('-Y',y1)
            y2w,y2h=dc.GetTextExtent('+Y')
            y2=wx.Point((width*np.cos((np.pi/180)*210))+xoffset,(height*np.sin((np.pi/180)*210))+yoffset)
            dc.DrawText('+Y',y2)
            z1=wx.Point(width*np.cos((np.pi/180)*330),height*np.sin((np.pi/180)*330))
            z2=wx.Point(width*np.cos((np.pi/180)*150),height*np.sin((np.pi/180)*150))
            dc.SetPen(self.pens['z'])
            dc.DrawLines([z1,z2],xoffset=xoffset,yoffset=yoffset)
            z1w,z1h=dc.GetTextExtent('-Z')
            z1=wx.Point((width*np.cos((np.pi/180)*330))+xoffset-z1w,(height*np.sin((np.pi/180)*330))+yoffset)
            dc.DrawText('-Z',z1)
            z2w,z2h=dc.GetTextExtent('+Z')
            z2=wx.Point((width*np.cos((np.pi/180)*150))+xoffset,(height*np.sin((np.pi/180)*150))+yoffset-z2h)
            dc.DrawText('+Z',z2)
    def UpdateDrawing(self):
        self.dc.set(wx.MemoryDC())
        self.Refresh(eraseBackground=False)
        self.Update()
    def UpdateMouse(self,event):
        self.old_mouse_coord=self.new_mouse_coord
        self.new_mouse_coord=(event.GetX()/self.zoom,event.GetY()/self.zoom)
        center_x,center_y=(self.GetSize()/self.zoom)/2
        point=(self.new_mouse_coord[0]-center_x-self.offset_coord[0],
               self.new_mouse_coord[1]-center_y-self.offset_coord[1])
        self.hovered_tile=pixel_to_hex(point,self.zoom)
        if event.Dragging():
            self.is_dragging=True
            self.lock.acquire()
            self.offset_coord=(self.offset_coord[0]+(self.new_mouse_coord[0]-self.old_mouse_coord[0]),self.offset_coord[1]+(self.new_mouse_coord[1]-self.old_mouse_coord[1]))
            self.lock.release()
            self.UpdateDrawing()
        elif event.LeftDown():
            self.is_left_click_down=True
        elif event.LeftUp():
            self.is_dragging=False
            self.is_left_click_down=False
class SelectedTileControlPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.main_sizer=wx.BoxSizer(orient=wx.VERTICAL)
        self.selected_tile_label=wx.StaticText(self,label='Selected Tile')
        self.selected_tile_x_label=wx.StaticText(self,label='X:')
        self.selected_tile_x_control=wx.SpinCtrl(self,min=-100)
        self.selected_tile_y_label=wx.StaticText(self,label='Y:')
        self.selected_tile_y_control=wx.SpinCtrl(self,min=-100)
        self.selected_tile_z_label=wx.StaticText(self,label='Z:')
        self.selected_tile_z_control=wx.SpinCtrl(self,min=-100)
        self.selected_tile_coord_sizer=wx.BoxSizer()
        self.selected_tile_coord_sizer.Add(self.selected_tile_x_label,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_x_control,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_y_label,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_y_control,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_z_label,0,wx.EXPAND)
        self.selected_tile_coord_sizer.Add(self.selected_tile_z_control,0,wx.EXPAND)
        self.main_sizer.Add(self.selected_tile_label,0,wx.EXPAND)
        self.main_sizer.Add(self.selected_tile_coord_sizer,0,wx.EXPAND)
        self.selected_tile_type_control=wx.RadioBox(self,choices=['Movement Cost 1','Movement Cost 2','Not Passable'])
        self.main_sizer.Add(self.selected_tile_type_control,0,wx.EXPAND)
        self.SetSizer(self.main_sizer)
        self.Show(True)
    def init(self,hexmap,lock):
        self.hexmap=hexmap
        self.lock=lock
class HexMapControlPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.main_sizer=wx.BoxSizer(orient=wx.VERTICAL)
        self.radius_label=wx.StaticText(self,label='Radius:')
        self.radius_control=wx.SpinCtrl(self,value='1')
        self.radius_sizer=wx.BoxSizer()
        self.radius_sizer.Add(self.radius_label,1,wx.EXPAND)
        self.radius_sizer.Add(self.radius_control,1,wx.EXPAND)
        self.main_sizer.Add(self.radius_sizer,0,wx.EXPAND)
        self.zoom_label=wx.StaticText(self,label='Zoom:')
        self.zoom_control=wx.SpinCtrl(self,value='10')
        self.zoom_sizer=wx.BoxSizer()
        self.zoom_sizer.Add(self.zoom_label,1,wx.EXPAND)
        self.zoom_sizer.Add(self.zoom_control,1,wx.EXPAND)
        self.main_sizer.Add(self.zoom_sizer,0,wx.EXPAND)
        self.notation_type_control=wx.RadioBox(self,choices=['None','Cube','Axial'])
        self.main_sizer.Add(self.notation_type_control,0,wx.EXPAND)
        self.selected_tile_control_panel=SelectedTileControlPanel(self)
        self.main_sizer.Add(self.selected_tile_control_panel,0,wx.EXPAND)
        self.SetSizer(self.main_sizer)
        self.Show(True)
    def init(self,hexmap,lock):
        self.hexmap=hexmap
        self.lock=lock
        self.selected_tile_control_panel.init(self.hexmap,self.lock)
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,-1,'HexMap Demo',size=(1920,1080))
        self.CreateStatusBar()
        self.hexmap_control_panel=HexMapControlPanel(self)
        self.render_panel=RenderPanel(self)
        self.main_sizer=wx.BoxSizer()
        self.main_sizer.Add(self.hexmap_control_panel,0,wx.EXPAND)
        self.main_sizer.Add(self.render_panel,1,wx.EXPAND)
        self.SetSizer(self.main_sizer)
        self.Show(True)
    def init(self,hexmap,lock):
        self.hexmap=hexmap
        self.lock=lock
        self.hexmap_control_panel.init(self.hexmap,self.lock)
        self.render_panel.init(self.hexmap,self.lock)
class App:
    def __init__(self):
        self.app=wx.App()
        self.lock=threading.Lock()
        self.running=False
        self.radius=1
        self.hexmap=RadialMap(self.radius)
        self.main_frame=MainFrame()
        self.main_frame.init(self.hexmap,self.lock)
        self.draw_thread=threading.Thread(target=self.drawLoop)
        self.main_frame.hexmap_control_panel.radius_control.Bind(wx.EVT_SPINCTRL, self.SetRadius)
        self.main_frame.hexmap_control_panel.zoom_control.Bind(wx.EVT_SPINCTRL, self.SetZoom)
        self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_x_control.Bind(wx.EVT_SPINCTRL, self.SetSelectedTile)
        self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_y_control.Bind(wx.EVT_SPINCTRL, self.SetSelectedTile)
        self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_z_control.Bind(wx.EVT_SPINCTRL, self.SetSelectedTile)
        self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.Bind(wx.EVT_RADIOBOX, self.SetSelectedTileType)
        self.main_frame.render_panel.Bind(wx.EVT_LEFT_DOWN,self.RenderPanelLeftMouseDown)
        self.main_frame.hexmap_control_panel.notation_type_control.Bind(wx.EVT_RADIOBOX, self.SetNotationType)
    def mainLoop(self):
        self.running=True
        self.draw_thread.start()
        self.main_frame.render_panel.UpdateDrawing()
        self.app.MainLoop()
    def drawLoop(self):
        while self.running:
            self.main_frame.render_panel.UpdateDrawing()
    def SetRadius(self,event):
        self.radius=self.main_frame.hexmap_control_panel.radius_control.GetValue()
        self.hexmap.reset(self.radius)
    def SetZoom(self,event):
        self.main_frame.render_panel.zoom=self.main_frame.hexmap_control_panel.zoom_control.GetValue()
    def SetSelectedTile(self,event):
        x=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_x_control.GetValue()
        y=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_y_control.GetValue()
        z=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_z_control.GetValue()
        self.main_frame.render_panel.selected_tile=Cube(x,y,z)
        tile=self.hexmap[Cube(x,y,z)]
        if tile!=False:
            if tile.isPassable!=False:
                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(2)
            elif tile.movement_cost==1:
                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(0)
            elif tile.movement_cost==2:
                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(1)
    def SetSelectedTileType(self,event):
        choice=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.GetString(self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.GetSelection())
        x=self.main_frame.render_panel.selected_tile.x
        y=self.main_frame.render_panel.selected_tile.y
        z=self.main_frame.render_panel.selected_tile.z
        tile=self.hexmap[Cube(x,y,z)]
        if tile!=False:
            if choice=='Movement Cost 1':
                tile.movement_cost=1
            elif choice=='Movement Cost 2':
                tile.movement_cost=2
            if choice=='Not Passable':
                tile.isPassable=False
    def RenderPanelLeftMouseDown(self,event):
        tile=self.hexmap[Cube(self.main_frame.render_panel.hovered_tile.x,self.main_frame.render_panel.hovered_tile.y,self.main_frame.render_panel.hovered_tile.z)]
        if tile!=False:
            self.main_frame.render_panel.selected_tile=self.main_frame.render_panel.hovered_tile
            self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_x_control.SetValue(self.main_frame.render_panel.selected_tile.x)
            self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_y_control.SetValue(self.main_frame.render_panel.selected_tile.y)
            self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_z_control.SetValue(self.main_frame.render_panel.selected_tile.z)
            if tile.isPassable==False:
                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(2)
            elif tile.movement_cost==1:
                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(0)
            elif tile.movement_cost==2:
                self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_type_control.SetSelection(1)
    def SetNotationType(self,event):
        choice=self.main_frame.hexmap_control_panel.notation_type_control.GetString(self.main_frame.hexmap_control_panel.notation_type_control.GetSelection())
        self.main_frame.render_panel.notation_type=choice
if __name__=='__main__':
    app=App()
    app.mainLoop()
