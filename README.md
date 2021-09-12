# iDNTR
Secondary development based on DNTR, Gmsh &amp; ParaView. (Desensitization)
---

1. **预期功能**

   - 给定文件路径，读入并结构化*.msh文件
   - 将网格数据转换为ANSYS格式的xy.dat和ii.dat文件
   - 读取用户输入的INPUT.DAT文件，与网格进行校对
   - 运行DNTR程序，读取OUTPUT.DAT文件
   - 将通量分布数据转换为*.vtk文件
   - 利用setting.json文件进行脚本设置
   - ~~记录日志文件~~
     - 时间
     - 文件名
     - 错误类型
---

2. **实现方法**

   - 读入msh文件

     - 文件格式：Gmsh - *.msh
     - ~~gmsh-sdk的gmsh python API ? https://www.cnpython.com/qa/300042~~
     - ~~自行编写msh格式读取函数~~已编写，但出于简洁性考虑在released版本中弃用
     - 利用meshio读取

   - 改写dat文件

     - 文件格式：Ansys - *.dat
     - 根据算例文件推测数据结构，自行编写

   - 读取INPUT.DAT文件和OUTPUT.DAT文件
      
      - 根据算例文件推测数据结构，自行编写
      
   - 改写vtk文件
   
      - 利用meshio的cell_data参数写入

   - ~~setting.json配置文件~~
---

3. **文件格式**

   - *.msh 文件 - 由Gmsh生成

     ```python
     $MeshFormat
     	version		file-type	data-size
     $ENdMeshFormat
     
     $PhysicalNames
     	numPhysicalNames
     	Dimension	PhysicalTag	"name"
     	...
     $EndPhysicalNames
     
     $Entities
     	numPoints	numCurves	numSurfaces	numVolumes
     	pointTag	X	Y	Z	numPhysicalTags	physicalTag(if exists)
     	...
     	curveTag	minX	minY	minZ	maxX	maxY	maxZ					numPhysicalTags	physicalTag	numBoundingPoints	pointTag(+-)
     	...
     	surfaceTag	minX	minY	minZ	maxX	maxY	maxZ
     		numPhysicalTags	physicalTag	numBoundingCurves	curveTag(+-)
     	...
     	volumeTag	minX	minY	minZ	maxX	maxY	maxZ
     		numPhysicalTags	physicalTag	numBoundingSurfaces	surfaceTag(+-)
     	...
     $EndEntities
     
     $PatitionedEntities
     $EndPartitonedEntities
     
     $Nodes
     	numEntitiesBlocks	numNodes	minNodeTag	maxNodeTag
     	entityDim	entityTag	parametric	numNodesInBlock
     	nodeTag
     	...
     	x	y	z
     	...
     	...
     $EndNodes
     
     $Elements
     	numEntitiesBlock	numElements	minElementTag	maxElementTag
         entityDim	entityTag	elementType	numElementsInBlocks
      		elementTag	nodeTag(many)
     		...
      	...
      $EndElements
      
      $Periodic
      $EndPeriodic
      
      $GhostElements
      $EndGhostElements
      
      $Parametrizations
      $EndParametrizations
      
      $NodeData
      $EndNodeData
      
      $ElementData
      $EndElementData
      
      $InterpolationScheme
      $EndInterpolationScheme
     ```


​     

   - *.dat 文件 - 由Ansys Mechanical APDL生成

     - II.DAT 文件


     ```python
     # II.DAT文件
     # list -> elements -> nodes + attributes
     
      LIST ALL SELECTED ELEMENTS.  (LIST NODES)
     
     	ELEM MAT TYP REL ESY SEC        NODES
     
         elem 
         
     	...
     ```

     - XY.DAT 文件

     ```python
     # XY.DAT文件
     # list -> nodes -> coordinates only
     
       LIST ALL SELECTED NODES.   DSYS=  0
     	
     	SORT TABLE ON  NODE  NODE  NODE
     
     	NODE		X		Y		Z
     
         nodeTag		x		y		z	(.11*digits)
         
     	...
     ```
---
### References
[1] DNTR
[2] Gmsh
[3] ParaView
[4] MSH File Format
[5] VTK File Formats
