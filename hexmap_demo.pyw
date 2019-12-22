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
def pixel_to_hex(point):
    q=((2./3)*point[0])/100
    r=(((-1./3)*point[0])+(np.sqrt(3)/3)*point[1])/100
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
class AxisBitmap:
    def __init__(self,parent):
        self.parent=parent
        self.current_mode='None'
    @property
    def width(self):
        return self.parent.GetSize()[0]//8
    @property
    def height(self):
        return self.parent.GetSize()[1]//8
    @property
    def size(self):
        return (self.width,self.width) if self.width<self.height else (self.height,self.height)
    @property
    def x(self):
        return 0
    @property
    def y(self):
        return self.parent.GetSize()[1]-self.size[1]
    @property
    def center_x(self):
        return self.size[0]/2
    @property
    def center_y(self):
        return self.size[1]/2
    def OnSize(self):
        self.axis_image=wx.Bitmap(self.size)
        if self.current_mode=='Cube':
            self.DrawCubic()
        elif self.current_mode=='Axial':
            self.DrawAxial()
        else:
            dc=wx.MemoryDC()
            dc.SelectObject(self.axis_image)
            dc.Clear()
    def SetMode(self,choice):
        self.current_mode=choice
        self.OnSize()
    def DrawCubic(self):
        dc=wx.MemoryDC()
        dc.SelectObject(self.axis_image)
        dc.Clear()
        text_sizes={
            '+X':dc.GetTextExtent('+X'),
            '-X':dc.GetTextExtent('-X'),
            '+Y':dc.GetTextExtent('+Y'),
            '-Y':dc.GetTextExtent('-Y'),
            '+Z':dc.GetTextExtent('+Z'),
            '-Z':dc.GetTextExtent('-Z')
        }
        line_axis={
            'X':(wx.Point((self.size[0]/2)*np.cos((np.pi/180)*180),(self.size[1]/2)*np.sin((np.pi/180)*180)),
                 wx.Point((self.size[0]/2)*np.cos((np.pi/180)*0),(self.size[1]/2)*np.sin((np.pi/180)*0))),
            'Y':(wx.Point((self.size[0]/2)*np.cos((np.pi/180)*210),(self.size[1]/2)*np.sin((np.pi/180)*210)),
                 wx.Point((self.size[0]/2)*np.cos((np.pi/180)*30),(self.size[1]/2)*np.sin((np.pi/180)*30))),
            'Z':(wx.Point((self.size[0]/2)*np.cos((np.pi/180)*330),(self.size[1]/2)*np.sin((np.pi/180)*330)),
                 wx.Point((self.size[0]/2)*np.cos((np.pi/180)*150),(self.size[1]/2)*np.sin((np.pi/180)*150)))
        }
        text_axis={
            'X':(wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*180))+self.center_x,((self.size[1]/2)*np.sin((np.pi/180)*180))+self.center_y-(text_sizes['-X'][1]/2)),
                 wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*0))+self.center_x-(text_sizes['+X'][0]),((self.size[1]/2)*np.sin((np.pi/180)*0))+self.center_y-(text_sizes['+X'][1]/2))),
            'Y':(wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*30))+self.center_x-text_sizes['-Y'][0]-(text_sizes['-Y'][0]/2),((self.size[1]/2)*np.sin((np.pi/180)*30))+self.center_y-text_sizes['-Y'][1]),
                 wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*210))+self.center_x,((self.size[1]/2)*np.sin((np.pi/180)*210))+self.center_y)),
            'Z':(wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*330))+self.center_x-text_sizes['-Z'][0],((self.size[1]/2)*np.sin((np.pi/180)*330))+self.center_y),
                 wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*150))+self.center_x,((self.size[1]/2)*np.sin((np.pi/180)*150))+self.center_y-text_sizes['+Z'][1]))
        }
        pen_axis={
            'X':self.parent.pens['x'],
            'Y':self.parent.pens['y'],
            'Z':self.parent.pens['z']
        }
        for axis in ['X','Y','Z']:
            dc.SetPen(pen_axis[axis])
            dc.DrawLines(line_axis[axis],xoffset=self.center_x,yoffset=self.center_y)
            dc.DrawText('-{}'.format(axis),text_axis[axis][0])
            dc.DrawText('+{}'.format(axis),text_axis[axis][1])
    def DrawAxial(self):
        dc=wx.MemoryDC()
        dc.SelectObject(self.axis_image)
        dc.Clear()
        text_sizes={
            '+X':dc.GetTextExtent('+X'),
            '-X':dc.GetTextExtent('-X'),
            '+Y':dc.GetTextExtent('+Y'),
            '-Y':dc.GetTextExtent('-Y')
        }
        line_axis={
            'X':(wx.Point((self.size[0]/2)*np.cos((np.pi/180)*180),(self.size[1]/2)*np.sin((np.pi/180)*180)),
                 wx.Point((self.size[0]/2)*np.cos((np.pi/180)*0),(self.size[1]/2)*np.sin((np.pi/180)*0))),
            'Y':(wx.Point((self.size[0]/2)*np.cos((np.pi/180)*210),(self.size[1]/2)*np.sin((np.pi/180)*210)),
                 wx.Point((self.size[0]/2)*np.cos((np.pi/180)*30),(self.size[1]/2)*np.sin((np.pi/180)*30)))
        }
        text_axis={
            'X':(wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*180))+self.center_x,((self.size[1]/2)*np.sin((np.pi/180)*180))+self.center_y-(text_sizes['-X'][1]/2)),
                 wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*0))+self.center_x-(text_sizes['+X'][0]),((self.size[1]/2)*np.sin((np.pi/180)*0))+self.center_y-(text_sizes['+X'][1]/2))),
            'Y':(wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*30))+self.center_x-text_sizes['-Y'][0]-(text_sizes['-Y'][0]/2),((self.size[1]/2)*np.sin((np.pi/180)*30))+self.center_y-text_sizes['-Y'][1]),
                 wx.Point(((self.size[0]/2)*np.cos((np.pi/180)*210))+self.center_x,((self.size[1]/2)*np.sin((np.pi/180)*210))+self.center_y))
        }
        pen_axis={
            'X':self.parent.pens['x'],
            'Y':self.parent.pens['y']
        }
        for axis in ['X','Y']:
            dc.SetPen(pen_axis[axis])
            dc.DrawLines(line_axis[axis],xoffset=self.center_x,yoffset=self.center_y)
            dc.DrawText('-{}'.format(axis),text_axis[axis][0])
            dc.DrawText('+{}'.format(axis),text_axis[axis][1])
    def Draw(self,dc):
        dc.DrawBitmap(self.axis_image,self.x,self.y)
class RenderPanel(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self,parent)
        self.parent=parent
        self.offset_coord=(0,0)
        self.old_mouse_coord=(0,0)
        self.new_mouse_coord=(0,0)
        self.is_dragging=False
        self.is_left_click_down=False
        self.selected_tile=Cube(0,0,0)
        self.hovered_tile=Cube(0,0,0)
        self.notation_type='None'
        self.text_colours={
            'X':wx.Colour('green'),
            'Y':wx.Colour('pink'),
            'Z':wx.Colour(30,144,155)
        }
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
        self.axis_bitmap=AxisBitmap(self)
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
        return [(((100)*np.cos((np.pi/180)*(60*i))),
                 ((100)*np.sin((np.pi/180)*(60*i)))) for i in range(0,6)]
    def OnPaint(self,event):
        wx.BufferedPaintDC(self,self.buffer)
    def OnSize(self,event):
        self.buffer=wx.Bitmap(*self.GetSize())
        self.axis_bitmap.OnSize()
        self.UpdateDrawing()
    def Draw(self,dc):
        dc.SelectObject(self.buffer)
        dc.SetBackground(self.brushes['background'])
        dc.Clear()
        self.lock.acquire()
        height=(100)*np.sqrt(3)
        width=(100)*2
        center_x,center_y=(self.GetSize())/2
        for x,y,z in Iterators.RingIterator(self.hexmap.radius,6):
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
            text_sizes={
                'X':dc.GetTextExtent(str(x)),
                'Y':dc.GetTextExtent(str(y)),
                'Z':dc.GetTextExtent(str(z))
            }
            if self.notation_type=='Cube':
                cubic_coordinates={
                    'X':(x_coord+center_x+self.offset_coord[0]-(text_sizes['X'][0]/2),-y_coord+center_y+self.offset_coord[1]-(height/3)),
                    'Y':(x_coord+center_x+self.offset_coord[0]-(width/4),-y_coord+center_y+self.offset_coord[1]+(height/4)-text_sizes['Y'][1]),
                    'Z':(x_coord+center_x+self.offset_coord[0]+(width/4)-text_sizes['Z'][0],-y_coord+center_y+self.offset_coord[1]+(height/4)-text_sizes['Z'][1])
                }
                for coord,axis in zip([x,y,z],['X','Y','Z']):
                    dc.SetTextForeground(self.text_colours[axis])
                    dc.DrawText(str(coord),cubic_coordinates[axis][0],cubic_coordinates[axis][1])
            elif self.notation_type=='Axial':
                axial_coordinates={
                    'X':(x_coord+center_x+self.offset_coord[0]-(width/4),-y_coord+center_y+self.offset_coord[1]-(text_sizes['X'][1]/2)),
                    'Y':(x_coord+center_x+self.offset_coord[0]+(width/4)-text_sizes['Y'][0],-y_coord+center_y+self.offset_coord[1]-(text_sizes['Y'][1]/2))
                }
                dc.DrawText(str(x),axial_coordinates['X'][0],axial_coordinates['X'][1])
                dc.DrawText(str(y),axial_coordinates['Y'][0],axial_coordinates['Y'][1])
        self.axis_bitmap.Draw(dc)
        self.lock.release()
    def UpdateDrawing(self):
        self.dc.set(wx.MemoryDC())
        self.Refresh(eraseBackground=False)
        self.Update()
    def UpdateMouse(self,event):
        self.old_mouse_coord=self.new_mouse_coord
        self.new_mouse_coord=(event.GetX(),event.GetY())
        center_x,center_y=(self.GetSize())/2
        point=(self.new_mouse_coord[0]-center_x-self.offset_coord[0],
               self.new_mouse_coord[1]-center_y-self.offset_coord[1])
        self.hovered_tile=pixel_to_hex(point)
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
        #self.zoom_label=wx.StaticText(self,label='Zoom:')
        #self.zoom_control=wx.SpinCtrl(self,value='1')
        #self.zoom_sizer=wx.BoxSizer()
        #self.zoom_sizer.Add(self.zoom_label,1,wx.EXPAND)
        #self.zoom_sizer.Add(self.zoom_control,1,wx.EXPAND)
        #self.main_sizer.Add(self.zoom_sizer,0,wx.EXPAND)
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
        #self.main_frame.hexmap_control_panel.zoom_control.Bind(wx.EVT_SPINCTRL, self.SetZoom)
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
    #def SetZoom(self,event):
        #self.main_frame.render_panel.zoom=self.main_frame.hexmap_control_panel.zoom_control.GetValue()
    def SetSelectedTile(self,event):
        x=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_x_control.GetValue()
        y=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_y_control.GetValue()
        z=self.main_frame.hexmap_control_panel.selected_tile_control_panel.selected_tile_z_control.GetValue()
        self.main_frame.render_panel.selected_tile=Cube(x,y,z)
        tile=self.hexmap[Cube(x,y,z)]
        if tile!=False:
            if not tile.isPassable:
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
        self.main_frame.render_panel.axis_bitmap.SetMode(choice)
if __name__=='__main__':
    app=App()
    app.mainLoop()
