# DNTRG
Secondary development based on DNTR, Gmsh &amp; ParaView. (Desensitization)

### 1. *transmsh.py*

1. **预期功能**

   - 给定文件路径，读入并结构化*.msh文件
   - 转换为ANSYS的*.dat文件
   - 利用setting.json文件进行脚本设置
   - 记录日志文件
     - 时间
     - 文件名
     - 错误类型

2. **实现方法**

   - 读入文件

     - 文件格式：Gmsh - *.msh
     - **?** gmsh-sdk的gmsh python API ? https://www.cnpython.com/qa/300042

   - 改写文件

     - 文件格式：Ansys - *.dat

   - setting.json配置文件

     - 内置库 json

     - 编码函数 json.dumps()

       ``````python
       import json
       
       json.dumps(obj, skipkey=False, ensure_ascii=True, indent=0, separators=(item_separator=',', dict_separator=':'), encoding='utf-8', sort_keys=False)
        
       # 参数含义：
       # obj:需转换为json的对象，为python内置数据结构，内置数据会按照对应法则转换为js数据结构，如(list, tuple)->array
       # skipkey:若为True，则遇到非python内置数据类型的对象时报错TypeError；若为Fasle，则跳过之
       # ensure_ascii:若为True，遇到非ascii编码时显示为u\xxxx
       # indent:若为0，在不换行；若不为0，则每个对象换行，且缩进为indent值
       # separators:对象分隔符，键值对分隔符
       # encoding:编码
       # sort_keys:是否按键排序
       ``````

     - 解码函数 json.loads()

       ```python
       json.loads(obj)
       # obj:需转换为python内置数据类型的json数据
       ```

   - 日志模块

     - 内置库 logging

       ```python
       import logging
       
       # 日志级别
       ```

    - 其他

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

     

***To be continued ...***

