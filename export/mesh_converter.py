from contextlib import contextmanager
import bpy


@contextmanager
def convert(obj, context, scene):
    """
    Create a (possibly temporary) mesh from an object.
    If the mesh is temporary, it is guaranteed to be removed when the calling block ends.
    Use it like this:

    with mesh_converter.convert(obj, context, scene) as mesh:
        if mesh:
            print(mesh.name)
            ...
    """

    mesh = None
    temporary = False

    try:
        if _need_to_convert_mesh(obj):
            # We have to apply modifiers and/or convert to mesh
            apply_modifiers = True
            modifier_mode = "PREVIEW" if context else "RENDER"

            edge_split_mod = _begin_autosmooth_if_required(obj)
            temporary = True
            mesh = obj.to_mesh(scene, apply_modifiers, modifier_mode)
            _end_autosmooth_if_required(obj, edge_split_mod)
        else:
            # No modifiers and the object.data is already a mesh
            mesh = obj.data
            if not mesh.tessfaces:
                mesh.calc_tessface()
        yield mesh
    finally:
        if mesh and temporary:
            bpy.data.meshes.remove(mesh, do_unlink=False)


def _need_to_convert_mesh(obj):
    in_editmode = obj.mode == "EDIT" or obj.data.is_editmode
    # Use gettattr with fallback because not every datablock
    # has the use_auto_smooth attribute
    needs_autosmooth = getattr(obj.data, "use_auto_smooth", False)

    return (in_editmode or needs_autosmooth
            or obj.modifiers or obj.type != "MESH"
            or obj.data.shape_keys)


def _begin_autosmooth_if_required(obj):
    if not getattr(obj.data, "use_auto_smooth", False):
        return None

    # We use an edge split modifier, it does the same as auto smooth
    # The only drawback is that it does not handle custom normals
    mod = obj.modifiers.new("__LUXCORE_AUTO_SMOOTH__", 'EDGE_SPLIT')
    mod.split_angle = obj.data.auto_smooth_angle
    return mod


def _end_autosmooth_if_required(obj, mod):
    if mod:
        obj.modifiers.remove(mod)
