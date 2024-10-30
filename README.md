# Summary of algorithm

### insertion

![insert_algorithm](https://github.com/user-attachments/assets/25dbf6fe-2474-4155-a3d7-3716370ef0f1)

### search

![search_algorithm](https://github.com/user-attachments/assets/a10af849-e29e-4585-925f-c1c3ddb465cf)

### range search

![range_search_algorithm](https://github.com/user-attachments/assets/dc33ea27-9c50-4bb0-8b6a-89de92940d12)

### deletion

![delete_algorithm](https://github.com/user-attachments/assets/f8c4a72c-39e2-4196-8c1b-c8793695cb13)

# Detailed descriptions of source code

### class Node

**멤버 변수**

```python
id: node가 가지는 고유 번호
m: node 내 key의 개수
keys: key들의 배열, 배열 내 key들은 오름차순으로 정렬되어 있다.
isLeaf: 이 노드가 leaf node인지를 판단하는 boolean
b: create 명령어로 입력 받은 최대 자식 노드의 개수
maxKeys: 노드가 가질 수 있는 최대 키의 개수 (b - 1과 동일)
minKeys: 노드가 가져야 하는 최소 키의 개수 (ceil(b / 2) - 1과 동일)
parent: 부모 노드에 대한 포인터
```

### class InternalNode

- Node 클래스를 상속받습니다.

**Node 클래스에서 정의된 멤버 변수 외 추가로 갖는 멤버 변수**

```python
children: child node들의 배열. 
					children[i]는 keys[i]의 left child를 가리키는 포인터이다. 
					keys[i]는 child[i]와 child[i+1] 사이에 위치한다.
r: rightmost child node를 가리키는 포인터
```

**멤버 함수**

- insert
    
    Internal node에서 키를 비교하며 어느 자식 노드로 내려갈지 결정한 후, leaf node에 도달하면 키를 삽입합니다. 
    
    노드에 키가 넘칠 경우 split을 통해 분할을 수행합니다.
    
    - internal node에서 키를 비교하며 어느 자식 노드로 내려갈지 결정합니다.
        
        ```python
              idx = 0
              while idx < len(self.keys) and key > self.keys[idx]:
                  idx += 1
        ```
        
        삽입할 키보다 노드 내에서 큰 key를 발견할 때까지 idx를 증가시킵니다.
        
        중복 키를 방지하기 위해 이미 노드 내에 존재하는 키가 발견되면 삽입을 중단합니다.
        
    - leaf node에 도달하면 삽입합니다.
        
        ```python
              if idx < len(self.children) and self.children[idx].isLeaf:
                  self.children[idx].insert(key, value)
        ```
        
        leaf node 내에서 key를 오름차순으로 유지하기 위해 위에서 찾은 idx에 키를 삽입합니다.
        
        idx가 node의 children 배열의 길이보다 작으면 children[idx]에 키를 삽입합니다.
        
    - idx가 children 배열의 길이와 같으면 rightmost child에 키를 삽입합니다.
        
        ```python
              elif idx == len(self.keys) and self.r is not None:
                  self.r.insert(key, value)
        ```
        
    - 삽입 후 노드 내에 키가 넘친다면 split을 진행합니다.
        
        ```python
              if len(self.keys) > self.maxKeys:
                  return self.split()
        ```
        
- split
    
    가운데 key를 부모 노드로 승천시키고, 노드를 좌우로 분할합니다. 
    
    부모 노드가 없으면 새로운 부모 노드를 생성하여 root를 교체합니다.
    
    - 가운데 key를 부모 노드로 승천시킵니다.
        
        ```python
              midIdx = len(self.keys) // 2
              midKey = self.keys[midIdx] # 가운데 키는 부모 노드로 승천
        ```
        
    - 가운데 key를 기준으로 key를 좌우분할 합니다.
        
        ```python
              # 가운데 키를 기준으로 노드를 좌우 분할
              # 새로운 노드로 기존 노드의 오른쪽 절반을 이동
              
              newRightNode = InternalNode(self.b)
              # 오른쪽 절반 키를 새로운 노드로 이동
              newRightNode.keys = self.keys[midIdx + 1 :] 
               # 오른쪽 절반 키의 자식 노드도 새로운 노드로 이동
              newRightNode.children = self.children[midIdx + 1 :]
              newRightNode.r = self.r
               # 키의 개수 설정
              newRightNode.m = len(newRightNode.keys)
        
              # 기존 노드에는 왼쪽 절반 정보만 남겨둠
              self.keys = self.keys[: midIdx]
              # 기존 노드의 왼쪽 절반 키의 자식 노드만 남겨둠
              self.children = self.children[: midIdx + 1] 
              # 키의 개수 설정
              self.m = len(self.keys) 
              self.r.parent = newRightNode
              # 왼쪽 노드의 rightmost children 설정
              self.r = self.children.pop() 
        ```
        
        internal node에서 일어나는 좌우분할이므로 가운데 key는 부모 node에 승천 후 기존 노드에 남겨두지 않습니다.
        
    - 분할된 노드가 root인 경우 새로운 root node를 생성 후 새로운 root에 키를 삽입합니다.
        
        ```python
              if self.parent is None:
                  newParentNode = InternalNode(self.b)
                  newParentNode.keys = [midKey]
                  newParentNode.children = [self]
                  newParentNode.m = 1 # 새롭게 만들어진 부모 노드에는 1개의 키만 존재하므로
                  newParentNode.r = newRightNode
                  # 새로운 부모 노드를 부모 포인터로 참조
                  self.parent = newParentNode 
                  newRightNode.parent = newParentNode 
        
        					# 새로운 부모 노드를 리턴해서 tree의 새로운 root를 지정할 수 있도록 한다.
                  return newParentNode
        ```
        
    - 분할된 노드의 부모 node가 존재하는 경우 부모 node에 키를 삽입합니다.
        
        ```python
              else:
                  # 부모 노드에 승천할 키가 이미 존재하는지 여부를 나타내는 flag
                  duplicatedFlag = False
                  # 가운데 키가 부모 노드에서 들어갈 적절한 위치를 찾음
                  idx = 0
                  while idx < len(self.parent.keys) and midKey >= self.parent.keys[idx]:
                      if midKey == self.parent.keys[idx]:
                          duplicatedFlag = True
                          break
                      idx += 1
                      
        			    # 분할된 오른쪽 노드의 부모 노드 지정
                  newRightNode.parent = self.parent 
                  # 부모 노드에 승천될 키가 존재하지 않는 경우에만 삽입 진행
                  if not duplicatedFlag:
        	            # 가운데 키 부모 노드에 삽입
                      self.parent.keys.insert(idx, midKey) 
                      # 부모 노드의 키 개수 업데이트
                      self.parent.m = len(self.parent.keys) 
        
        					# 부모 노드의 가장 마지막에 승천된 키가 삽입된다면 
        					# newRightNode는 부모 노드의 rightmost child가 된다.
                  if idx == len(self.parent.keys) - 1: 
                      self.parent.children.insert(idx, self)
                      self.parent.r = newRightNode
                  else:
        	            # 오른쪽 분할 노드를 부모 노드의 새로운 자식으로 설정
                      self.parent.children.insert(idx + 1, newRightNode) 
        ```
        
    - 부모 node에 key를 삽입 후 넘친다면 부모 node에서도 재귀적으로 분할을 진행합니다.
        
        ```python
                  if len(self.parent.keys) > self.parent.maxKeys:
                      return self.parent.split()
        ```
        

- delete
    
    Internal 노드에서 key를 삭제할 때 해당 key를 left subtree의 최대 key 값으로 교체합니다. 
    
    삭제 후 병합 또는 키 재분배가 필요할 경우 부모 또는 형제 노드와의 병합을 통해 균형을 맞춥니다.
    
    - internal node에 존재하는 key에 delete가 일어난다면 그 key를 해당 node의 left subtree key의 최댓값으로 교체합니다.
        
        ```python
        			 	  idx = 0
        	        while self.keys[idx] != key:
        	            idx += 1
        	            
        	        # left child가 존재하는 경우 left subtree의 최댓값을 구한다.
        	        leftMax = 0
        	        if self.children[idx]:
        	            # left child의 rightmost child로만 이동한다.
        	            # leaf에 도달하면 그 node의 마지막 key 값을 리턴한다.
        	            findNode = self.children[idx]
        	            while not findNode.isLeaf:
        	                findNode = findNode.r
        	
        	            leftMax = findNode.keys[len(findNode.keys) - 1]
        	            self.keys[idx] = leftMax
        ```
        

- merge
    
    left 또는 right sibling과 병합합니다. 
    
    병합 후 키가 넘칠 경우 다시 split을 진행하며, 새로운 root를 생성해야 하는 경우 root를 갱신합니다.
    
    - merge가 일어나야 하는 현재 node가 부모의 leftmost child가 아니라면 **left sibling과 병합**을 진행합니다.
        
        ```python
                    # 부모 키를 가져오고 병합
                    leftSiblingNode.keys.append(parentNode.keys[idx - 1])
                    leftSiblingNode.keys.extend(self.keys)
                    # children도 병합
                    leftSiblingNode.children.append(leftSiblingNode.r)
                    leftSiblingNode.children.extend(self.children)
                    
                    ...
                    
                    # 현재 노드가 rightmost child가 아닌 경우 left sibling의 r 포인터를 갱신
                    if self.r:
                        self.r.parent = leftSiblingNode
                        leftSiblingNode.r = self.r
                    # 현재 노드가 rightmost child인 경우 부모 노드의 r 포인터 갱신
                    else:
                        parentNode.r = leftSiblingNode
                        # 원래 leftSiblingNode가 children 배열의 마지막에 존재했는데, 
                        # leftSiblingNode가 병합으로 인해 rightmost children이 되었으므로 
                        # children배열에서 제거한다.
                        parentNode.children.pop()
                        leftSiblingNode.r = None
        ```
        
        병합 과정은 다음과 같습니다.
        
        - 왼쪽 node에 대응되는 부모 node의 키를 가져옵니다.
        - 현재 node의 key와 children을 왼쪽 node와 병합합니다.
        - 부모 node의 key와 children을 업데이트합니다.
    - 병합 후 병합된 node의 key가 넘치면 split을 진행합니다.
        
        ```python
                    # 병합 후 노드가 넘치면 split
                    if len(leftSiblingNode.keys) > leftSiblingNode.maxKeys:
                        leftSiblingNode.split()
        ```
        
    - 병합된 node가 새로운 root node라면 병합된 node를 리턴합니다.
        
        ```python
                    if leftSiblingNode.parent is None:
                        return leftSiblingNode
        
                    if len(self.parent.children) == 0:
                        self.parent = None
                        leftSiblingNode.parent = None
                        return leftSiblingNode
        ```
        
    - merge가 일어나야 하는 현재 node가 부모의 leftmost child가 이라면 **right sibling과 병합**을 진행합니다.
        
        ```python
                    # 부모 키를 가져오고 오른쪽 형제와 병합한다.
                    # 현재 노드에 합친다.
                    self.keys.append(parentNode.keys[idx])
                    self.keys.extend(rightSiblingNode.keys)
        
                    # 부모로부터 받아온 키의 child로 self.r을 설정해준다.
                    self.children.append(self.r)
                    # 이후 right sibling의 children을 병합한다.
                    self.children.extend(rightSiblingNode.children)
                    
                    ...
                    
                    # 부모 노드에서 키와 자식 삭제
                    del self.parent.keys[idx]
                    if len(parentNode.children) > 1:
        		            # rightSiblingNode는 현재 노드에 합쳐졌으니 rightSiblingNode 제거
                        del self.parent.children[idx + 1] 
                    else:
                        del self.parent.r
                        self.parent.r = self
                        self.parent.children.pop()
        ```
        
        병합 과정은 다음과 같습니다.
        
        - 현재 node에 대응되는 부모 node의 key를 현재 node로 가져옵니다.
        - right sibling의 key와 child를 현재 node에 병합합니다.
        - 부모 node의 key와 children을 업데이트합니다.
    - left sibling으로의 merge와 동일하게, 병합 후 node의 key가 넘치면 split을 진행합니다.
    - left sibling으로의 merge와 동일하게, 병합된 node가 새로운 root node라면 병합된 node를 리턴합니다.

### class LeafNode

**Node 클래스에서 정의된 멤버 변수 외 추가로 갖는멤버 변수**

```python
values: value들의 배열.
				values[i]는 keys[i]에 대응되는 값
r: right sibling을 가리키는 포인터
```

**멤버 함수**

- insert
    
    키를 삽입할 적절한 위치를 찾은 후, 키와 값을 삽입합니다. 
    
    중복 키는 허용되지 않으며, 삽입 후 키가 넘치면 split을 수행합니다.
    
    - node 내에서 key를 삽입하기 위한 적절한 위치를 찾습니다.
        
        ```python
                # 노드 내에 키를 삽입하기 위한 적절한 위치를 찾는다.
                idx = 0
                while idx < len(self.keys) and key > self.keys[idx]:
                    # 중복 키를 방지한다.
                    if key == self.keys[idx]:
                        print("Duplicated keys are not allowed")
                        return
                    idx += 1
        ```
        
        중복 key를 방지하기 위해 해당 node 내에 삽입할 key가 이미 존재한다면 “Duplicated keys are not allowed”를 출력하고 종료합니다.
        
    - key를 삽입한 후 노드가 넘친다면 split을 진행합니다.
        
        ```python
                self.keys.insert(idx, key)
                self.values.insert(idx, value)
        
                if len(self.keys) > self.maxKeys:
                    return self.split()
        ```
        

- split
    
    가운데 키를 기준으로 리프 노드를 분할하며, 부모 노드에 가운데 키를 복사하여 승천시킵니다. 
    
    부모 노드가 없을 경우 새로운 root 노드를 생성합니다.
    
    - leaf node에 tree의 모든 key가 존재해야 하므로 가운데 키를 기준으로 분할 후 가운데 키를 leaf node에 남겨두며 키를 복제해서 부모 노드에 승천시킵니다.
        
        ```python
                midIdx = len(self.keys) // 2
                midKey = self.keys[midIdx]
        
                # 가운데 키를 기준으로 노드를 좌우 분할
                # 가운데 키보다 오른쪽에 있는 키와 값들을 이동
                newRightNode = LeafNode(self.b)
                newRightNode.keys = self.keys[midIdx + 1 :]
                newRightNode.values = self.values[midIdx + 1 :]
                if self.r is not None: 
                    newRightNode.r = self.r
                newRightNode.m = len(newRightNode.keys)
                newRightNode.parent = self.parent 
        
                # 기존 노드에는 가운데 키와 값을 포함한 왼쪽 키와 값들만 남겨둔다.
                self.keys = self.keys[: midIdx + 1]
                self.values = self.values[: midIdx + 1]
                self.r = newRightNode
                self.m = len(self.keys)
        ```
        
    - split이 일어난 node가 root node여서 승천할 부모 node가 존재하지 않는다면 새로운 root node를 생성 후 가운데 키를 승천시킵니다.
        
        ```python
              # 부모 노드가 존재하지 않는다면 (루트인 경우) 새로운 부모 노드를 생성
              if self.parent is None:
                  newParentNode = InternalNode(self.b)
                  newParentNode.keys = [midKey]
                  newParentNode.children = [self]
                  newParentNode.m = 1 # 새롭게 만들어진 부모 노드에는 1개의 키만 존재하므로
                  newParentNode.r = newRightNode
                  # 새로운 부모 노드를 부모 포인터로 참조
                  self.parent = newParentNode 
                  newRightNode.parent = newParentNode 
        
                  return newParentNode
        ```
        
        tree의 root node를 갱신하기 위해 새로운 root node를 리턴합니다.
        
    - 분할된 노드의 부모 node가 존재하는 경우 부모 node에 키를 삽입합니다.
        
        ```python
        		
        			# 분할된 오른쪽 노드의 부모 노드 지정			
        	    newRightNode.parent = self.parent 
        	    if not duplicatedFlag:
        	        self.parent.keys.insert(idx, midKey) # 가운데 키 부모 노드에 삽입
        	        self.parent.m = len(self.parent.keys) # 부모 노드의 키 개수 업데이트
        			# 부모 노드의 가장 마지막에 승천된 키가 삽입된다면 
        			# newRightNode는 부모 노드의 rightmost child가 된다.
        	    if idx == len(self.parent.keys) - 1: 
        	        self.parent.children.insert(idx, self)
        	        self.parent.r = newRightNode
        	    else:
        		      # 오른쪽 분할 노드를 부모 노드의 새로운 자식으로 설정
        	        self.parent.children.insert(idx + 1, newRightNode) 
        ```
        
    - 부모 node에 key를 삽입 후 넘친다면 부모 node에서도 재귀적으로 분할을 진행합니다.
        
        ```python
              if len(self.parent.keys) > self.parent.maxKeys:
                  return self.parent.split()
        ```
        

- delete
    
    리프 노드에서 키를 삭제한 후, 최소 키 개수를 충족하지 못할 경우 형제 노드로부터 키를 재분배 받거나 형제와 병합합니다. 
    
    형제와 병합 후 부모 노드에서도 병합이 필요하다면 재귀적으로 부모 노드에서의 merge를 호출합니다.
    
    - 노드 내에서 삭제할 키가 몇 번째 인덱스에 존재하는지 찾고 지웁니다.
    - 루트 노드에서의 삭제가 일어났다면 종료합니다.
    - 루트 노드에서의 삭제가 아닌 경우 삭제 후 키가 최소 키 개수보다 많다면 종료합니다.
        
        ```python
            if len(self.keys) >= self.minKeys:
                # internal node에 그 키가 존재하면 internal node에서도 삭제한다.
                if not internalFlag:
                    return
        ```
        
    - 삭제 후 키가 최소 키보다 적은 경우 형제 노드로부터 키를 받습니다.
        
        ```python
            # 삭제할 키가 존재하는 노드가 leftmost child가 아닌 경우
            if deleteNodeIdx > 0:
                # left sibling의 키 개수를 비교한다.
                leftSiblingNode = parentNode.children[deleteNodeIdx - 1]
                # left sibling으로부터 키를 분배받을 수 있는 경우 분배 받는다.
                if len(leftSiblingNode.keys) > leftSiblingNode.minKeys:
        		        # left sibling의 max key를 지원받는다.
                    self.keys.insert(0, leftSiblingNode.keys.pop()) 
                    # value도 업데이트 한다.
                    self.values.insert(0, leftSiblingNode.values.pop()) 
                    # 삭제 할 키가 존재하는 노드와 left sibling 사이 부모의 key를 
                    # left sibling의 key의 최댓값으로 업데이트 한다.
                    parentNode.keys[deleteNodeIdx - 1] = leftSiblingNode.keys[-1] 
        
                    return
        ```
        
        - 우선 left sibling으로부터 key를 받을 수 있는지 확인합니다.
        - key를 받을 수 있다면  left sibling의 최대 key를 지원받고  left sibling에 대응되는 부모 노드의 key를 받은 key로 대체합니다.
        
        ```python
            # right sibling으로부터 분배받을 수 있는지 확인한다.
            # 삭제할 키가 존재하는 노드가 rightmost child가 아닌 경우
            if deleteNodeIdx < len(parentNode.children):
                # right sibling의 키 개수를 비교한다.
                rightSiblingNode = self.r
                if len(rightSiblingNode.keys) > rightSiblingNode.minKeys:
        		        # right sibling의 min key를 지원받는다.
                    self.keys.append(rightSiblingNode.keys[0]) 
                    # value도 업데이트 한다.
                    self.values.append(rightSiblingNode.values[0]) 
        
        						# 삭제 할 키가 존재하는 노드와 right sibling 사이 부모의 key를 
        						# right sibling의 최솟값으로 업데이트 한다.
                    parentNode.keys[deleteNodeIdx] = rightSiblingNode.keys[0] 
                    
        						# 지원받은 후 right sibling에서 지원해준 key 삭제
                    del rightSiblingNode.keys[0] 
                    # 지원받은 후 right sibling에서 지원해준 value 삭제
                    del rightSiblingNode.values[0] 
                    
                    return
        ```
        
        - left sibling으로부터 key를 받을 수 없는 경우 right sibling으로부터 key를 받을 수 있는지 확인합니다.
        - right sibling으로부터 key를 받을 수 있다면 최소 key를 지원받고 삭제할 key가 존재하는 노드에 대응되는 부모 node의 key를 right sibling으로부터 받은 key로 대체합니다.
        
        ```python
            # 양 옆 sibling들로부터 키를 분배받을 수 없는 경우
            # 부모 노드로부터 키를 지원받고 형제와 병합한다.
            newRoot = self.merge(deleteNodeIdx)
        ```
        
        - 양 옆 형제로부터 key를 받을 수 없는 경우 부모 노드로부터 키를 지원받고 형제 노드와 병합합니다.
    - internal node에도 해당 key가 있는 경우 삭제합니다.
        
        ```python
            # internal node에도 해당 키가 존재하는 경우 internal node에서 지운다.
            if internalFlag:
                findNode = self.parent
                while findNode is not None:
                    if findNode.keys.__contains__(key):
                        findNode.delete(key)
                    findNode = findNode.parent
        ```
        
- merge
    
    삭제 후 노드의 키가 부족할 때, 부모로부터 키를 받아서 left sibling 또는 right sibling과 병합합니다. 
    
    병합 후 새로운 root가 필요할 경우 root를 갱신합니다.
    
    - 병합이 필요한 node가 leftmost child가 아니라면 부모 key를 지원받은 후 left sibling과 병합합니다.
        
        ```python
            # leftmost child가 아닌 경우 left sibling과 병합
            if deleteNodeIdx > 0:
                # left sibling과 병합하는 경우 왼쪽 노드의 부모 key를 삭제한다.
                leftSiblingNode = parentNode.children[deleteNodeIdx - 1]
        
                # left sibling에 key와 value를 합친다.
                leftSiblingNode.keys = leftSiblingNode.keys + self.keys
                leftSiblingNode.values = leftSiblingNode.values + self.values
        
                # left sibling의 right sibling pointer를 갱신한다.
                if self.r:
                    leftSiblingNode.r = self.r
        
                # 현재 노드가 부모 노드의 rightmost child라면
                # left sibling과 병합한 후 left sibling이 새로운 rightmost child가 된다.
                # left sibling을 children 배열에서 제거하고 rightmost child로 설정해준다.
                if deleteNodeIdx == len(parentNode.keys):
                    parentNode.children.pop()
                    parentNode.r = leftSiblingNode
                # 현재 노드가 부모 노드의 rightmost child가 아니라면
                # left sibling과 병합되었으므로 현재 노드를 부모 노드의 children 배열에서 삭제한다.
                else:
                    del parentNode.children[deleteNodeIdx]
        
                # 현재 노드와 left sibling 사이에 해당하는 부모 노드의 key를 삭제한다.
                del parentNode.keys[deleteNodeIdx - 1]
                
                # 병합 후 부모 노드가 빈다면 병합된 노드가 트리의 새로운 루트 노드가 된다.
                if len(parentNode.keys) == 0 and parentNode.parent is None:
                    leftSiblingNode.parent = None
                    # 새로운 루트를 리턴한다.
                    return leftSiblingNode
        
        ```
        
    - 병합이 필요한 node가 leftmost child인 경우 부모 node로부터 key를 지원받은 후 right sibling과 병합합니다.
        
        ```python
            # right sibling과 병합하는 경우 지우려는 키가 있는 노드의 부모 key를 삭제한다.
            rightSiblingNode = self.r
            self.keys = self.keys + rightSiblingNode.keys
            self.values = self.values + rightSiblingNode.values
            if deleteNodeIdx + 1 < len(self.parent.children):
                parentNode.children[deleteNodeIdx + 1] = self
            else:
                self.parent.r = self
            self.r = rightSiblingNode.r
        
            del parentNode.keys[deleteNodeIdx]
            del parentNode.children[deleteNodeIdx]
        ```
        
    - 부모 node가 root node인 경우, 병합 후 부모 node의 key가 없게되면 병합된 node를 tree의 새로운 root로 갱신합니다.
        
        ```python
            if len(parentNode.keys) == 0 and parentNode.parent is None:
                self.parent = None
                # 새로운 루트를 리턴한다.
                return self
        ```
        
    - 부모 node가 root node가 아닌 경우, 병합 후 key가 부족해지면 부모 node에서도 재귀적으로 병합이 일어납니다.
        
        ```python
        	
            # 병합 후 부모 노드의 키가 부족하다면 재귀적으로 부모 노드에서도 병합이 필요하다.
            # 루트 노드인 경우는 제외한다.
            if len(parentNode.keys) < parentNode.minKeys and parentNode.parent is not None:
                parentIdx = 0
                while parentIdx < len(parentNode.parent.children) and parentNode.parent.children[parentIdx] != parentNode:
                    parentIdx += 1
                
                newRoot = parentNode.merge(parentIdx)  
                return newRoot
        ```
        
    

### Additional functions

- save_to_file
    
    트리 구조를 파일로 저장하는 함수입니다. 트리의 루트 노드부터 시작하여 모든 노드를 재귀적으로 순회하 각 노드의 정보를 파일에 기록합니다.
    
    - 매개변수
        - file_name: 트리가 저장될 인덱스 파일의 이름
        - append: 파일을 덮어쓸지 (true) 또는 추가할지 (false)를 결정하는 boolean
    - 기능
        - 트리의 루트 노드부터 시작하여 모든 노드를 순회하기 위해 `_save_tree_recursive`라는 재귀적 헬퍼 함수를 호출합니다. 이 함수는 트리의 노드 구조를 인덱스 파일에 기록합니다.

- _save_tree_recursive
    
    파일로부터 트리 구조를 복원하는 함수입니다. 각 노드의 정보를 읽어와 트리를 다시 구성하며, 부모와 자식 노드를 연결합니다.
    
    - 매개변수
        - node: 현재 처리 중인 노드
        - file_name: 트리가 저장될 인덱스 파일의 이름
    - 기능
        1. leaf node 
        
        ```python
        v = []
        for value in node.values:
            v.append(value.strip("'"))
        file.write(f"LeafNode {node.id} {node.keys};{v};{right_sibling_id}\n")
        ```
        
        - 리프 노드의 경우 노드 ID, 키 값 리스트, 저장된 값 리스트, 오른쪽 형제의 ID(있을 경우)가 파일에 기록됩니다.
        - `node.r`이 `None`일 경우, 즉 오른쪽 형제가 없을 경우 'None'으로 기록됩니다.
        - 각 노드의 값은 리스트로 저장되며, 쉼표로 구분된 문자열 형식으로 파일에 기록됩니다.
        1. internal node
        
        ```python
        children_ids = [child.id for child in node.children]
        file.write(f"InternalNode {node.id} {node.keys};{children_ids};{right_sibling_id}\n")
        ```
        
        - 내부 노드는 자식 노드들의 ID를 저장합니다. 즉, 자식 노드가 리스트 형태로 기록되며, 노드 ID가 쉼표로 구분된 문자열로 저장됩니다.
        - 마찬가지로 오른쪽 형제가 있을 경우 그 노드의 ID를 기록하고, 없을 경우 'None'으로 기록합니다.
    - index file 구조
        - 파일에는 각 노드가 다음과 같은 형식으로 기록됩니다.
            
            ```python
            InternalNode {node_id} {keys};{children};{rightmost_child_id}
            LeafNode {node_id} {keys};{values};{right_sibling_id}
            ```
            

- load_from_file
    
    파일의 첫 번째 줄에서 `b` 값을 읽어 트리의 최대 자식 수를 설정하며, 각 노드를 `node_map`에 저장한 후 부모-자식 관계를 설정합니다.
    
    - 매개변수
        - file_name: 데이터를 담고 있는 인덱스 파일의 이름.
    - 기능
        - 인덱스 파일로부터 트리 구조를 로드하는 함수입니다. 파일의 각 줄을 읽어와 노드들을 다시 연결하여 트리를 복원합니다. 노드 ID에 따라 노드를 map에 저장하고, 부모 자식 및 형제 관계를 설정합니다.
        - 인덱스 파일의 첫 번째 줄에는 트리에서 각 노드가 가질 수 있는 최대 키의 개수를 나타내는 `b` 값이 저장되어 있습니다. 이 값을 읽어와 트리의 b를 설정합니다.
        
        ```python
        self.b = int(lines[0].strip())
        ```
        
        - 인덱스 파일의 두 번째 줄부터 각 줄을 순차적으로 처리하면서 노드의 타입(LeafNode or InternalNode), ID, 키, value 또는 child ID 정보를 추출합니다. 추출한 정보를 바탕으로 해당 노드 객체를 생성하고 `node_map`에 저장합니다.
        
        ```python
        for line in lines[1:]:
            parts = line.strip().split(';')
            node_type, keys_str = parts[0].split(' ', 1)
            node_id_str, keys_list_str = keys_str.split(' ', 1)
            node_id = int(node_id_str)
            keys = list(map(int, keys_list_str.strip('[]').split(','))) if keys_list_str.strip('[]') else []
        ```
        
        - `node_type == "LeafNode"`의 경우 해당 줄의 정보를 바탕으로 리프 노드를 생성합니다. 오른쪽 형제 노드 ID는 나중에 처리되며, 형제가 있는지 없는지 여부만 기록합니다.
        
        ```python
        if node_type == "LeafNode":
            node = LeafNode(self.b)
            node.keys = keys
            values_str = parts[1].strip()
            node.values = values_str.strip('[]').split(', ') if values_str.strip('[]') else []
            node_map[node_id] = node
        ```
        
        - `node_type == "InternalNode"` 의 경우 자식 노드들의 ID를 저장할 공간을 미리 확보하고 노드 키를 설정합니다. 자식 ID는 나중에 처리하며 자식 노드 리스트는 빈 상태로 남겨둡니다.
        
        ```python
        elif node_type == "InternalNode":
            node = InternalNode(self.b)
            node.keys = keys
            node_map[node_id] = node
        ```
        
        - 노드 정보를 모두 생성한 후 파일의 각 줄을 다시 읽어서 자식 노드나 형제 노드가 있는 경우 해당 노드들 간의 관계를 `node_map`을 통해 설정합니다.

# Instructions for compiling source code

기능 별로 소스 코드를 실행하기 위해 다음 명령어를 터미널에 입력합니다.

입력 시 중괄호는 입력하지 않으며, 파일의 확장자까지 입력해야 합니다.

### creation

```python
python3 bptree.py -c {INDEX_FILE} {SIZE_OF_EACH_NODE}
```

- INDEX_FILE: 생성 할 인덱스 파일의 이름입니다. 기존에 해당 이름의 파일이 존재하면 그 파일을 덮어씌우고, 없다면 새롭게 생성합니다.
- SIZE_OF_EACH_NODE: 하나의 노드가 가질 수 있는 최대 자식 노드의 개수입니다.
    
   

### insertion

```python
python3 bptree.py -i {INDEX_FILE} {DATA_FILE}
```

creation을 통해 **인덱스 파일을 생성한 뒤** insertion 명령어를 입력해야 합니다.

- INDEX_FILE: creation 명령어를 통해 생성된 인덱스 파일의 이름입니다.
- DATA_FILE: 인덱스 파일에 입력될 key,value 쌍을 가진 입력 데이터 파일의 이름입니다.
    
   

### search

```python
python3 bptree.py -s {INDEX_FILE} {KEY}
```

insertion을 통해 **인덱스 파일에 데이터를 입력한 뒤** search 명령어를 입력해야 합니다.

- INDEX_FILE: insertion 명령어를 통해 입력 데이터를 기반으로 만들어진 인덱스 파일의 이름입니다. 이 인덱스 파일에는 b+ tree 구조로 데이터가 저장되어 있습니다.
- KEY: 찾을 키의 번호입니다. KEY는 정수형이라고 가정합니다.
        

### range search

```python
python3 bptree.py -r {INDEX_FILE} {START_KEY} {END_KEY}
```

insertion을 통해 **인덱스 파일에 데이터를 입력한 뒤** range search 명령어를 입력해야 합니다.

- INDEX_FILE: insertion 명령어를 통해 입력 데이터를 기반으로 만들어진 인덱스 파일의 이름입니다. 이 인덱스 파일에는 b+ tree 구조로 데이터가 저장되어 있습니다.
- START_KEY: 찾을 키의 lowerbound입니다.
- END_KEY: 찾을 키의 upperbound입니다.

        

### deletion

```python
python3 bptree.py -d {INDEX_FILE} {DATA_FILE}
```

insertion을 통해 **인덱스 파일에 데이터를 입력한 뒤** deletion 명령어를 입력해야 합니다.

- INDEX_FILE: insertion 명령어를 통해 입력 데이터를 기반으로 만들어진 인덱스 파일의 이름입니다. 이 인덱스 파일에는 b+ tree 구조로 데이터가 저장되어 있습니다.
- DATA_FILE: 인덱스 파일에서 삭제할 key들이 담긴 데이터 파일의 이름입니다. key는 정수형이며, 각 key들은 엔터로 구분됩니다.
