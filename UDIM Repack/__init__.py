bl_info = {
    "name": "UDIM Repack Toolkit",
    "author": "Paint-a-Farm",
    "version": (1, 2),
    "blender": (2, 80, 0),
    "location": "UV > Unwrap > UDIM Repack",
    "description": "Tools for unpacking/repacking/selecting UDIM UVs",
    "warning": "",
    "doc_url": "",
    "category": "UV",
}

import bpy
import bmesh
from math import floor


class UdimRestore(bpy.types.Operator):
    bl_idname = "uv.udimrestore"
    bl_label = "Restore UDIM Locations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selection = context.selected_objects
        
        for obj in selection:
            me = obj.data
            bm = bmesh.from_edit_mesh(me)
            
            uv_layer = bm.loops.layers.uv[me.uv_layers.active.name]
            
            udim_original_x = bm.loops.layers.float.get('udim_x')
            udim_original_y = bm.loops.layers.float.get('udim_y')

            # adjust UVs
            for f in bm.faces:
                x = [p[uv_layer].uv[0] for p in f.loops]
                y = [p[uv_layer].uv[1] for p in f.loops]
                centroid = (sum(x) / len(f.loops), sum(y) / len(f.loops))
                
                for l in f.loops:
                    luv = l[uv_layer]
                    try:
                        luv.uv = (luv.uv[0]-floor(centroid[0])+floor(l[udim_original_x]), luv.uv[1]-floor(centroid[1])+floor(l[udim_original_y]))
                    except:
                        print('ignoring new face')

            bmesh.update_edit_mesh(me, False, False)

        return {'FINISHED'}

class UdimHome(bpy.types.Operator):
    bl_idname = "uv.udimhome"
    bl_label = "Create Home UV Map"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        selection = context.selected_objects

        for obj in selection:
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            uv_layer = bm.loops.layers.uv[me.uv_layers.active.name]
            
            uv_layername = obj.data.uv_layers.new(name=obj.data.uv_layers[0].name + ".Home").name
            uv_layer2 = bm.loops.layers.uv[uv_layername]

            # adjust UVs
            for f in bm.faces:
                x = [p[uv_layer].uv[0] for p in f.loops]
                y = [p[uv_layer].uv[1] for p in f.loops]
                centroid = (sum(x) / len(f.loops), sum(y) / len(f.loops))
                
                for l in f.loops:
                    luv = l[uv_layer]
                    l[uv_layer2].uv = (luv.uv[0]-floor(centroid[0]), luv.uv[1]-floor(centroid[1]))

            bmesh.update_edit_mesh(me, False, False)

        return {'FINISHED'}

class UdimStore(bpy.types.Operator):
    bl_idname = "uv.udimstore"
    bl_label = "Store UDIM Locations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selection = context.selected_objects

        for obj in selection:
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            uv_layer = bm.loops.layers.uv[me.uv_layers.active.name]

            udim_original_x = bm.loops.layers.float.get('udim_x')
            if udim_original_x is None:
                udim_original_x = bm.loops.layers.float.new('udim_x')

            udim_original_y = bm.loops.layers.float.get('udim_y')
            if udim_original_y is None:
                udim_original_y = bm.loops.layers.float.new('udim_y')

            # adjust UVs
            for f in bm.faces:
                x = [p[uv_layer].uv[0] for p in f.loops]
                y = [p[uv_layer].uv[1] for p in f.loops]
                centroid = (sum(x) / len(f.loops), sum(y) / len(f.loops))

                for l in f.loops:
                    l[udim_original_x] = centroid[0]
                    l[udim_original_y] = centroid[1]
                    
                    print('centroid', centroid)

            bmesh.update_edit_mesh(me, False, False)
        
        return {'FINISHED'}

class UdimSelectTile(bpy.types.Operator):
    bl_idname = "uv.udimselecttile"
    bl_label = "Select Similar By Tile"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selection = context.selected_objects

        centroids = []

        for obj in selection:
            me = obj.data
            bm = bmesh.from_edit_mesh(me)

            uv_layer = bm.loops.layers.uv[me.uv_layers.active.name]
            
            
            # adjust UVs
            for f in bm.faces:
                if f.select:
                    x = [p[uv_layer].uv[0] for p in f.loops]
                    y = [p[uv_layer].uv[1] for p in f.loops]
                    centroid = (sum(x) / len(f.loops), sum(y) / len(f.loops))
                    centroids.append((floor(centroid[0]), floor(centroid[1])))

        if len(centroids) > 0:
            for obj in selection:
                me = obj.data
                bm = bmesh.from_edit_mesh(me)

                uv_layer = bm.loops.layers.uv[me.uv_layers.active.name]
                
                # adjust UVs
                if len(centroids) > 0:
                    for f in bm.faces:
                        x = [p[uv_layer].uv[0] for p in f.loops]
                        y = [p[uv_layer].uv[1] for p in f.loops]
                        centroid = (sum(x) / len(f.loops), sum(y) / len(f.loops))
                        
                        if any(x[0] == floor(centroid[0]) and x[1] == floor(centroid[1]) for x in centroids):
                            f.select = True

                bmesh.update_edit_mesh(me, False, False)
        
        return {'FINISHED'}

class UdimRepackMenu(bpy.types.Menu): 	 
    bl_label = "UDIM Repack"	   
    bl_idname = "VIEW3D_MT_uv_map_udim_repack"
        
    def draw(self, context):
        layout = self.layout							 
        layout.operator(UdimStore.bl_idname, icon="RESTRICT_RENDER_OFF")
        layout.operator(UdimHome.bl_idname, icon="HOME")
        layout.operator(UdimRestore.bl_idname, icon="MOD_UVPROJECT")

    
def menu_func(self, context):
    self.layout.separator()
    self.layout.menu(UdimRepackMenu.bl_idname)

def select_menu_func(self, context):
    self.layout.separator()
    self.layout.operator(UdimSelectTile.bl_idname, icon="RESTRICT_SELECT_OFF")
    
def register():
    bpy.utils.register_class(UdimRepackMenu)
    bpy.utils.register_class(UdimRestore)
    bpy.utils.register_class(UdimHome)
    bpy.utils.register_class(UdimStore)
    bpy.utils.register_class(UdimSelectTile)
#    bpy.types.IMAGE_MT_uvs.append(menu_func)
    bpy.types.IMAGE_MT_uvs_context_menu.append(menu_func)
    bpy.types.IMAGE_MT_uvs_unwrap.append(menu_func)
    bpy.types.IMAGE_MT_select.append(select_menu_func)
    
def unregister():
    bpy.utils.unregister_class(UdimRepackMenu)
    bpy.utils.unregister_class(UdimRestore)
    bpy.utils.unregister_class(UdimHome)
    bpy.utils.unregister_class(UdimStore)
    bpy.utils.unregister_class(UdimSelectTile)
#    bpy.types.IMAGE_MT_uvs.remove(menu_func)
    bpy.types.IMAGE_MT_uvs_context_menu.remove(menu_func)
    bpy.types.IMAGE_MT_uvs_unwrap.remove(menu_func)
    bpy.types.IMAGE_MT_select.remove(select_menu_func)

if __name__ == "__main__":
    register()