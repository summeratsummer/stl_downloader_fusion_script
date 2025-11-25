import adsk.core, adsk.fusion, traceback
import os
import datetime

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        
        if not design:
            ui.messageBox('No active design found')
            return
        
        # Create export folder
        export_folder = create_export_folder()
        
        # Export all components as STL
        success_count = export_all_stl_files(design, export_folder, ui)
        
        ui.messageBox(f"STL Export Complete!\n\nExported {success_count} files to:\n{export_folder}")
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def create_export_folder():
    """Create a timestamped folder on Desktop for STL exports"""
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = f"Fusion_STL_Export_{timestamp}"
    export_path = os.path.join(desktop, folder_name)
    
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    
    return export_path

def sanitize_filename(name):
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name

def export_component_as_stl(component, export_path, ui):
    """Export a single component as STL"""
    try:
        # Sanitize the component name for filename
        safe_name = sanitize_filename(component.name)
        filename = f"{safe_name}.stl"
        file_path = os.path.join(export_path, filename)
        
        # Get the export manager
        export_mgr = component.parentDesign.exportManager
        
        # Create STL export options
        stl_options = export_mgr.createSTLExportOptions(component, file_path)
        
        # Set STL options
        stl_options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        stl_options.isBinaryFormat = True
        
        # Export the STL
        export_mgr.execute(stl_options)
        
        print(f"Exported: {filename}")
        return True
        
    except Exception as e:
        print(f"Failed to export {component.name}: {str(e)}")
        return False

def export_occurrence_as_stl(occurrence, export_path, ui):
    """Export a single occurrence as STL"""
    try:
        # Sanitize the occurrence name for filename
        safe_name = sanitize_filename(occurrence.name)
        filename = f"{safe_name}.stl"
        file_path = os.path.join(export_path, filename)
        
        # Get the export manager
        export_mgr = occurrence.component.parentDesign.exportManager
        
        # Create STL export options for the occurrence
        stl_options = export_mgr.createSTLExportOptions(occurrence, file_path)
        
        # Set STL options
        stl_options.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
        stl_options.isBinaryFormat = True
        
        # Export the STL
        export_mgr.execute(stl_options)
        
        print(f"Exported: {filename}")
        return True
        
    except Exception as e:
        print(f"Failed to export {occurrence.name}: {str(e)}")
        return False

def export_all_stl_files(design, export_path, ui):
    """Export all components and occurrences as individual STL files"""
    success_count = 0
    root = design.rootComponent
    
    # Export all unique components
    print("Exporting components as STL...")
    all_components = design.allComponents
    
    for component in all_components:
        # Skip the root component if it's empty
        if component == root and len(component.bRepBodies) == 0:
            continue
            
        if export_component_as_stl(component, export_path, ui):
            success_count += 1
    
    # Export occurrences as well (for assembly instances)
    print("Exporting occurrences as STL...")
    all_occurrences = root.allOccurrences
    
    for occurrence in all_occurrences:
        # Only export if the occurrence has geometry
        if occurrence.component.bRepBodies.count > 0:
            if export_occurrence_as_stl(occurrence, export_path, ui):
                success_count += 1
    
    # Create a summary file
    create_export_summary(design, export_path, success_count)
    
    return success_count

def create_export_summary(design, export_path, success_count):
    """Create a summary text file with export details"""
    summary_path = os.path.join(export_path, "EXPORT_SUMMARY.txt")
    
    with open(summary_path, 'w') as f:
        f.write("FUSION 360 STL EXPORT SUMMARY\n")
        f.write("=" * 50 + "\n")
        f.write(f"Export Date: {datetime.datetime.now()}\n")
        f.write(f"Design Name: {design.rootComponent.name}\n")
        f.write(f"Total Files Exported: {success_count}\n")
        f.write(f"Export Location: {export_path}\n")
        f.write("\n")
        f.write("EXPORTED FILES:\n")
        f.write("-" * 30 + "\n")
        
        # List all STL files in the folder
        stl_files = [f for f in os.listdir(export_path) if f.endswith('.stl')]
        for stl_file in sorted(stl_files):
            f.write(f"{stl_file}\n")
        
        f.write("\n")
        f.write("NOTES:\n")
        f.write("- Files are exported in binary STL format\n")
        f.write("- High mesh refinement used for quality\n")
        f.write("- Invalid characters in names replaced with '_'\n")

# Alternative simpler version - exports only visible components
def export_visible_components_only(design, export_path, ui):
    """Export only the root component and its direct children (simpler approach)"""
    success_count = 0
    root = design.rootComponent
    
    print("Exporting visible components as STL...")
    
    # Export the root component if it has bodies
    if root.bRepBodies.count > 0:
        if export_component_as_stl(root, export_path, ui):
            success_count += 1
    
    # Export all occurrences in the root
    for occurrence in root.occurrences:
        if occurrence.component.bRepBodies.count > 0:
            if export_occurrence_as_stl(occurrence, export_path, ui):
                success_count += 1
    
    return success_count

# If you want to use the simpler version, replace the export_all_stl_files call with:
# success_count = export_visible_components_only(design, export_folder, ui)