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

"""
                         TASK GRAPH
                            │
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
            Bake        Accumulate        Pack
              │             │              │
              └─────────────┼──────────────┘
                            │
                            ▼
                       ImageHandle
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
            OutputArtifact          TileSet
                  │                   │
                  ▼                   ▼
                Disk             ImageBuffer
                                      │
                                      ▼
                                    NumPy

                            ▲
                            │
                     ImageResource
                            │
                            ▼
                      bpy.types.Image
"""
If code needs to manipulate an output image, it gets an ImageHandle.
If code needs to know what that output represents or where it is stored, it uses handle.artifact.
If code needs pixels, it asks handle.tiles() / handle.buffer(tile).
If code needs Blender, it asks handle.image().
