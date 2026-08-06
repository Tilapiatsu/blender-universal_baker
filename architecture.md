"""
                 Planner
                    │
                    ▼
              OutputRepository
                    │
                    ▼
               ImageHandle
        ┌───────────┼────────────┐
        ▼           ▼            ▼
 OutputArtifact ImageResource ImageBuffer cache
        │           │            │
        ▼           ▼            ▼
      Disk      Blender Image   NumPy
"""

* OutputArtifact answers where the logical image lives and how it's named (including UDIM expansion).
* ImageResource answers how to interact with Blender (bpy.types.Image), but only when baking or previewing.
* ImageBuffer represents raw pixel data for a single tile and is the only object compositors and packers need to manipulate.
* ImageHandle orchestrates those three representations, performing lazy loading, caching, saving, invalidation, and synchronization.
* OutputRepository simply indexes and returns ImageHandle instances; it no longer needs to understand buffers, tiles, Blender images, or caching policies.
