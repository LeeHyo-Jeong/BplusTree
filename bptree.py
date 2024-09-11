import argparse

find_route = [] # search시 leaf까지 내려가는데 통과한 노드의 키들을 담는 배열
val = 0       # search를 통해 찾은 key에 대응하는 value를 담는 변수

class Node:
    # 클래스 내에서 전역적으로 사용되는 카운터
    # 노드가 몇 개 생성되었는지를 나타낸다.
    # 각 노드에 번호를 매기기 위해 사용된다.
    _id_counter = 0

    def __init__(self, b):
        self.id = Node._get_next_id()
        self.m = 0                  # key의 개수
        self.keys = []              # key들의 배열, 오름차순으로 정렬되어 있다. p를 keys와 (children 또는 values)로 나누어서 구현한다.
        self.isLeaf = False         # 이 노드가 leaf node인지를 판단하는 boolean
        self.b = b                  # create 명령어로 입력 받은 최대 자식 노드의 개수
        self.maxKeys = b - 1        # 노드가 가질 수 있는 최대 키의 개수 (b - 1과 동일)
        self.minKeys = (b // 2) - 1 # 노드가 가져야 하는 최소 키의 개수
        self.parent = None          # 부모 노드에 대한 포인터

    @classmethod
    def _get_next_id(cls):
        # index file을 읽어서 트리를 만들 때 용이하게 하기 위해 노드마다 고유한 id 부여
        next_id = cls._id_counter
        cls._id_counter += 1
        return next_id


class InternalNode(Node):
    def __init__(self, b):
        super().__init__(b)
        self.children = []  # children[i]는 keys[i]의 left child를 가리키는 포인터, keys[i]는 child[i]와 child[i+1] 사이에 위치한다.
        self.r = None       # rightmost child node를 가리키는 포인터
        self.isLeaf = False
        self.maxKeys = b - 1

    def insert(self, key, value):
        # internal node에서 키를 비교하며 어느 자식 노드로 내려갈지 결정한다.
        idx = 0
        while idx < len(self.keys) and key > self.keys[idx]:
            idx += 1

        # leaf node에 도달하면 삽입
        if idx < len(self.children) and self.children[idx].isLeaf:
            self.children[idx].insert(key, value)
        elif idx == len(self.keys) and self.r is not None:
            self.r.insert(key, value)
        else:
            if idx < len(self.children):
                self.children[idx].insert(key, value)
            elif idx == len(self.keys) and self.r is not None:
                self.r.insert(key, value)
                

        if len(self.keys) > self.maxKeys:
            return self.split()
        
        # 현재 노드가 루트라면 루트 반환.
        # 루트가 분할되지 않아도 새롭게 루트를 갱신하기 위한 로직.
        if self.parent is None:
            return self


    def split(self):
        midIdx = len(self.keys) // 2
        midKey = self.keys[midIdx] # 가운데 키는 부모 노드로 승천

        
        # 가운데 키를 기준으로 노드를 좌우 분할
        # 새로운 노드로 기존 노드의 오른쪽 절반을 이동
        newRightNode = InternalNode(self.b)
        newRightNode.keys = self.keys[midIdx + 1 :] # 오른쪽 절반 키를 새로운 노드로 이동
        newRightNode.children = self.children[midIdx + 1 :] # 오른쪽 절반 키의 자식 노드도 새로운 노드로 이동
        newRightNode.r = self.r # 요거 추가함
        newRightNode.m = len(newRightNode.keys) # 키의 개수 설정

        # 기존 노드에는 왼쪽 절반 정보만 남겨둠
        self.keys = self.keys[: midIdx] # 기존 노드에 왼쪽 절반 키만 남겨둠
        self.children = self.children[: midIdx + 1] # 기존 노드의 왼쪽 절반 키의 자식 노드만 남겨둠
        self.m = len(self.keys) # 키의 개수 설정
        self.r.parent = newRightNode
        self.r = self.children.pop() # 왼쪽 노드의 rightmost children 설정

        # 분할된 노드들의 child들의 parent 포인터를 다시 설정
        for child in newRightNode.children:
            child.parent = newRightNode

        for child in self.children:
            child.parent = self
        
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


        # 부모 노드가 존재한다면 부모 노드에 가운데 키 승천
        else:
            # 가운데 키가 부모 노드에서 들어갈 적절한 위치를 찾음
            duplicatedFlag = False
            idx = 0
            while idx < len(self.parent.keys) and midKey >= self.parent.keys[idx]:
                if midKey == self.parent.keys[idx]:
                    duplicatedFlag = True
                    break
                idx += 1
    
            newRightNode.parent = self.parent # 분할된 오른쪽 노드의 부모 노드 지정
            if not duplicatedFlag:
                self.parent.keys.insert(idx, midKey) # 가운데 키 부모 노드에 삽입
                self.parent.m = len(self.parent.keys) # 부모 노드의 키 개수 업데이트

            if idx == len(self.parent.keys) - 1: # 부모 노드의 가장 마지막에 승천된 키가 삽입된다면 newRightNode는 부모 노드의 rightmost child가 된다.
                self.parent.children.insert(idx, self)
                self.parent.r = newRightNode
            else:
                self.parent.children.insert(idx + 1, newRightNode) # 오른쪽 분할 노드를 부모 노드의 새로운 자식으로 설정

            if len(self.parent.keys) > self.parent.maxKeys:
                return self.parent.split()
        
        return None
    
    def delete(self, key):
        # internal node에 트리에서 지우고자 하고 있는 키가 있다면 left subtree의 최대 키 값으로 교체
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
  
    def merge(self, idx):
        # internal node의 merge 과정
        parentNode = self.parent

        # leftmost child가 아닌 경우 left sibling과 병합
        if idx > 0:
            leftSiblingNode = parentNode.children[idx - 1]
            # 부모 키를 가져오고 병합
            leftSiblingNode.keys.append(parentNode.keys[idx - 1])
            leftSiblingNode.keys.extend(self.keys)
            # children도 병합
            leftSiblingNode.children.append(leftSiblingNode.r)
            leftSiblingNode.children.extend(self.children)

            if parentNode.keys[idx - 1] == 845:
                print("-----")

            # 왼쪽 노드를 가리키는 부모 키 제거
            del parentNode.keys[idx - 1]
            if idx < len(parentNode.children):
                # 왼쪽 노드로 합쳐졌으므로 현재 키 제거
                del parentNode.children[idx]

            # 현재 노드가 rightmost child인 경우 왼쪽 노드를 새로운 rightmost child로 설정한다.
            elif idx == len(parentNode.children):
                parentNode.r = leftSiblingNode

            '''
            # 현재 노드가 rightmost child가 아닌 경우
            if idx < len(parentNode.children):
                # 부모 노드에서 키와 자식 삭제
                del self.parent.keys[idx]
                del self.parent.children[idx]

            # 현재 노드가 rightmost child인 경우 병합된 왼쪽 노드를 rightmost child로 설정한다.
            elif idx == len(parentNode.children):
                del parentNode.keys[idx - 1]
                del parentNode.children[idx - 1]
                parentNode.r = leftSiblingNode
            '''

            # 왼쪽 노드로 합쳐졌으므로 자식들의 parent를 leftSibling으로 갱신
            for child in self.children:
                child.parent = leftSiblingNode

            # 현재 노드가 rightmost child가 아닌 경우 left sibling의 r 포인터를 갱신
            if self.r:
                self.r.parent = leftSiblingNode
                leftSiblingNode.r = self.r
            # 현재 노드가 rightmost child인 경우 부모 노드의 r 포인터 갱신
            else:
                parentNode.r = leftSiblingNode
                # 원래 leftSiblingNode가 children 배열의 마지막에 존재했는데, leftSiblingNode가 병합으로 인해 rightmost children이 되었으므로 children배열에서 제거한다.
                parentNode.children.pop()
                leftSiblingNode.r = None

            # 병합 후 노드가 넘치면 split
            if len(leftSiblingNode.keys) > leftSiblingNode.maxKeys:
                leftSiblingNode.split()
            
            if leftSiblingNode.parent is None:
                return leftSiblingNode

            if len(self.parent.children) == 0:
                self.parent = None
                leftSiblingNode.parent = None
                return leftSiblingNode
            
        # leftmost child인 경우 right sibling과 병합
        else:
            if len(parentNode.children) > 1:
                rightSiblingNode = parentNode.children[idx + 1]
            else:
                rightSiblingNode = parentNode.r
            # 부모 키를 가져오고 오른쪽 형제와 병합한다.
            # 현재 노드에 합친다.
            self.keys.append(parentNode.keys[idx])
            self.keys.extend(rightSiblingNode.keys)

            # 부모로부터 받아온 키의 child로 self.r을 설정해준다.
            self.children.append(self.r)
            # 이후 right sibling의 children을 병합한다.
            self.children.extend(rightSiblingNode.children)

            # 합쳐진 노드의 r을 원래 rightSiblingNode의 r로 설정
            if rightSiblingNode.r:
                self.r = rightSiblingNode.r
                rightSiblingNode.r.parent = self
            else:
                self.r = None

            # 부모 노드에서 키와 자식 삭제
            del self.parent.keys[idx]
            if len(parentNode.children) > 1:
                del self.parent.children[idx + 1] # rightSiblingNode는 현재 노드에 합쳐졌으니 rightSiblingNode 제거
            else:
                del self.parent.r
                self.parent.r = self
                self.parent.children.pop()

            # 병합 후 노드가 넘치면 split
            if len(self.keys) > self.maxKeys:
                self.split()

            if self.parent is None:
                return self

            if len(self.parent.children) == 0:
                self.parent = None
                # 새로운 루트인 self를 리턴
                return self

        # 부모 노드가 루트 노드가 아닌 경우 부모 노드에 키가 부족해진다면 재귀적으로 병합 진행
        if len(parentNode.keys) < parentNode.minKeys and parentNode.parent is not None:
            parentIdx = parentNode.parent.children.index(parentNode)
            parentNode.merge(parentIdx)

class LeafNode(Node):
    def __init__(self, b):
        super().__init__(b)
        self.values = []    # values[i]는 keys[i]에 대응되는 값
        self.r = None       # right sibling을 가리키는 포인터
        self.isLeaf = True  
        self.maxKeys = b - 1

    def insert(self, key, value):
        # 노드 내에 키를 삽입하기 위한 적절한 위치를 찾는다.
        idx = 0
        while idx < len(self.keys) and key > self.keys[idx]:
            # 중복 키를 방지한다.
            if key == self.keys[idx]:
                print("Duplicated keys are not allowed")
                return
            idx += 1

        self.keys.insert(idx, key)
        self.values.insert(idx, value)

        if len(self.keys) > self.maxKeys:
            return self.split()

        self.m += 1
        
    def split(self): # 가운데 키를 기준으로 분할 후 가운데 키를 leaf node에 남겨두며 키를 복제해서 부모 노드에 승천시켜야 한다.
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

        if self.parent is None:
            newParentNode = InternalNode(self.b) # 부모 노드는 leaf가 아닌 internal node
            newParentNode.keys = [midKey]
            newParentNode.children = [self]
            newParentNode.r = newRightNode
            newParentNode.m = 1
            self.parent = newParentNode
            newRightNode.parent = newParentNode

            return newParentNode

        else:
            duplicatedFlag = False
            # 부모 노드에 키를 삽입할 적절한 위치를 찾는다.
            idx = 0
            while idx < len(self.parent.keys) and midKey >= self.parent.keys[idx]:
                if self.parent.keys[idx] == midKey:  # 중복 키 발견 시 삽입하지 않고 리턴
                    duplicatedFlag = True
                    break
                idx += 1      
            
            if not duplicatedFlag:
                self.parent.keys.insert(idx, midKey)
                self.parent.m = len(self.parent.keys)

            newRightNode.parent = self.parent

            if idx == len(self.parent.keys) - 1: # 부모 노드의 가장 마지막에 승천된 키가 삽입된다면 newRightNode는 부모 노드의 rightmost child가 된다.
                self.parent.children.insert(idx, self) # 기존의 rightmost child는 부모 노드의 children으로
                self.parent.r = newRightNode # 새로운 rightmost child 지정
            else:
                self.parent.children.insert(idx + 1, newRightNode)

            if len(self.parent.keys) > self.parent.maxKeys:
                return self.parent.split()
            
        return None
    
    def delete(self, key, internalFlag): # 삭제할 키, 삭제할 키가 internal node에도 존재하는지 여부를 나타내는 flag
        # 노드 내에서 삭제할 키가 몇 번째 인덱스에 존재하는지 찾고 지운다.
        idx = 0
        newRoot = None
        while idx < len(self.keys):
            if self.keys[idx] == key:
                del self.keys[idx]
                del self.values[idx]
                break
            idx += 1

        # 루트 노드인 경우 삭제 후 종료한다.
        if self.parent is None:
            return
        
        # 삭제 후 키가 최소 키 개수보다 많다면 종료한다.
        if len(self.keys) >= self.minKeys:
            # 삭제 후 키가 최소 키 개수보다 많아도 internal node에 그 키가 존재하면 internal node에서도 삭제 해야한다.
            if not internalFlag:
                return
        
        else:
            '''삭제 후 키가 최소 키 개수보다 적은 경우'''
            # left sibling에서 키를 분배받을 수 있는지 확인하기 위해 left sibling을 찾는다.
            parentNode = self.parent
            # 삭제할 키가 존재하는 노드가 parent의 몇 번째 자식인지 찾는다.
            deleteNodeIdx = 0
            while deleteNodeIdx < len(parentNode.keys):
                if parentNode.children[deleteNodeIdx] == self:
                    break
                deleteNodeIdx += 1
            
            # 삭제할 키가 존재하는 노드가 leftmost child가 아닌 경우
            if deleteNodeIdx > 0:
                # left sibling의 키 개수를 비교한다.
                leftSiblingNode = parentNode.children[deleteNodeIdx - 1]
                # left sibling으로부터 키를 분배받을 수 있는 경우 분배 받는다.
                if len(leftSiblingNode.keys) > leftSiblingNode.minKeys:
                    self.keys.insert(0, leftSiblingNode.keys.pop()) # left sibling의 max key를 지원받는다.
                    self.values.insert(0, leftSiblingNode.values.pop()) # value도 업데이트 한다.
                    parentNode.keys[deleteNodeIdx - 1] = leftSiblingNode.keys[-1] # 삭제 할 키가 존재하는 노드와 left sibling 사이 부모의 key를 left sibling의 key의 최댓값으로 업데이트 한다.

                    return
                
            # left sibling으로부터 키를 분배받을 수 없는 경우 right sibling으로부터 분배받을 수 있는지 확인한다.
            # 삭제할 키가 존재하는 노드가 rightmost child가 아닌 경우
            if key == 1:
                print("FFF")
            if deleteNodeIdx < len(parentNode.children):
                # right sibling의 키 개수를 비교한다.
                rightSiblingNode = self.r
                if len(rightSiblingNode.keys) > rightSiblingNode.minKeys:
                    self.keys.append(rightSiblingNode.keys[0]) # right sibling의 min key를 지원받는다.
                    self.values.append(rightSiblingNode.values[0]) # value도 업데이트 한다.

                    parentNode.keys[deleteNodeIdx] = rightSiblingNode.keys[0] # 삭제 할 키가 존재하는 노드와 right sibling 사이 부모의 key를 right sibling의 최솟값으로 업데이트 한다.

                    del rightSiblingNode.keys[0] # 지원받은 후 right sibling에서 지원해준 key 삭제
                    del rightSiblingNode.values[0] # 지원받은 후 right sibling에서 지원해준 value 삭제
                    
                    return

            # 양 옆 sibling들로부터 키를 분배받을 수 없는 경우 부모 노드로부터 키를 지원받고 형제와 병합한다.
            newRoot = self.merge(deleteNodeIdx)

        # internal node에도 해당 키가 존재하는 경우 internal node에서 지운다.
        if internalFlag:
            findNode = self.parent
            while findNode is not None:
                if findNode.keys.__contains__(key):
                    findNode.delete(key)
                findNode = findNode.parent

        if newRoot:
            return newRoot # 새롭게 바뀐 루트가 있는 경우 리턴
        return None


    def merge(self, deleteNodeIdx):
        parentNode = self.parent
        leftSiblingNode = None
        rightSiblingNode = None

        # leftmost child가 아닌 경우 left sibling과 병합
        if deleteNodeIdx > 0:
            # left sibling과 병합하는 경우 왼쪽 노드의 부모 key를 삭제한다.
            leftSiblingNode = parentNode.children[deleteNodeIdx - 1]

            # left sibling이 leftmost children이 아닌 경우 left sibling의 left sibling의 r 포인터를 다시 설정한다.
            if deleteNodeIdx - 2 > 0:
                parentNode.children[deleteNodeIdx - 2].r = self
            self.keys = leftSiblingNode.keys + self.keys
            self.values = leftSiblingNode.values + self.values

            if deleteNodeIdx == len(parentNode.keys):
                parentNode.r = self

            # 왼쪽 노드의 부모 key를 삭제했을 때 부모 노드의 key 개수가 부족해진다면 merge
            #if deleteNodeIdx - 1 == self.parent.minKeys:
            #    parentNode.merge(deleteNodeIdx - 1)

            # 부족해지지 않는 경우
            # 왼쪽 노드의 부모 key를 삭제한다.
            #else: 
            del parentNode.keys[deleteNodeIdx - 1]
            del parentNode.children[deleteNodeIdx - 1]


            if len(parentNode.keys) == 0 and parentNode.parent is None:
                self.parent = None
                # 새로운 루트를 리턴한다.
                return self
            
        # leftmost node인 경우 right sibling과 병합
        else: 
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

            if len(parentNode.keys) == 0 and parentNode.parent is None:
                self.parent = None
                # 새로운 루트를 리턴한다.
                return self

        # 병합 후 부모 노드의 키가 부족하다면 재귀적으로 부모 노드에서도 병합이 필요하다.
        # 루트 노드인 경우는 제외한다.
        if len(parentNode.keys) < parentNode.minKeys and parentNode.parent is not None:
            parentIdx = 0
            while parentIdx < len(parentNode.parent.children) and parentNode.parent.children[parentIdx] != parentNode:
                parentIdx += 1
            
            newRoot = parentNode.merge(parentIdx)  
            return newRoot

        return None

class BPlusTree:
    def __init__(self, b):
        self.root = LeafNode(b)
        self.b = b
    
    def insert(self, key, value):
        new_root = self.root.insert(key, value)
        if new_root != None:
            self.root = new_root
        else:
            # 새로운 루트가 반환되지 않더라도 부모가 없으면 루트를 갱신
            while self.root.parent is not None:
                self.root = self.root.parent

    def search(self, key):
        global find_route
        global val
        find_route = []
        findNode = self.root
        if findNode is None:
            return None
        
        internalFlag = False # 해당 키가 internal node에도 존재하는지 여부를 나타내는 flag이다.

        # leaf까지 내려간다.
        while findNode is not None and not findNode.isLeaf:
            # print(str(findNode.keys).strip('[]'))
            find_route.append(str(findNode.keys).strip('[]'))
            # 타고 내려갈 적절한 child node를 찾는다.
            childIdx = 0
            while childIdx < len(findNode.keys) and key >= findNode.keys[childIdx]:
                if findNode.keys[childIdx] == key: # internal node에 해당 키가 존재하면 그 키가 있는 위치의 child node에 찾고자 하는 키가 존재한다.
                    internalFlag = True
                    break
                childIdx += 1

            # rightmost child도 비교한다.
            # 모든 left children들의 키들보다 찾으려는 키가 큰 경우 rightmost child로 내려간다.
            if childIdx == len(findNode.keys) and findNode.r:
                findNode = findNode.r
            else:
                findNode = findNode.children[childIdx]
        
        # 도달한 leaf node 안에서 해당 키가 존재하는지 찾는다.
        find_route.append(str(findNode.keys).strip('[]'))
        # print(str(findNode.keys).strip('[]')) # 도달한 leaf node의 키 출력
        keyIdx = 0
        while keyIdx < len(findNode.keys):
            if findNode.keys[keyIdx] == key:
                # 트리 안에 키가 존재하는 경우 그 키에 대응하는 값을 리턴
                # return findNode.values[keyIdx]
                # 트리 안에 키가 존재하는 경우 그 키가 존재하는 노드를 리턴
                val = (findNode.values[keyIdx].strip('"')).strip("'")
                return findNode, internalFlag
            keyIdx += 1
        
        # 트리 안에 키가 존재하지 않는 경우 None을 리턴
        return None
    
    def range_search(self, lowerBound, upperBound):
        # 키의 lower bound와 upper bound가 주어지면 그 범위 내에 해당하는 key와 value를 리턴한다.

        findNode = self.root
        if findNode is None:
            return None
        
        # lowerbound를 기준으로 leaf까지 내려간다.
        while findNode is not None and not findNode.isLeaf:
            # 타고 내려갈 적절한 chlild node를 찾는다.
            childIdx = 0
            while childIdx < len(findNode.children) and lowerBound > findNode.keys[childIdx]:
                childIdx += 1
            
            # rightmost child도 비교한다.
            if childIdx == len(findNode.children) and findNode.r:
                findNode = findNode.r

            else:
                findNode = findNode.children[childIdx]

        # leaf node의 right sibling을 가리키는 포인터를 타고 범위 탐색을 한다.
        while findNode is not None:
            idx = 0
            while idx < len(findNode.keys):
                if lowerBound <= findNode.keys[idx] <= upperBound:
                    print(f"{findNode.keys[idx]}, {findNode.values[idx].strip('\'\'')}")
                idx += 1
            findNode = findNode.r

    def delete(self, key):
        result = self.search(key)
        if result is None:
            print(f"Given key {key} does not exist in the tree")
            return 
        deleteNode, internalFlag = result[0], result[1]

        deleteNode, internalFlag = self.search(key) # 삭제 할 키가 존재하는 노드와 그 키가 internal node에도 존재하는지 여부
        
        if deleteNode is None:
            print("Given key does not exist in the tree")
            return
        
        newRoot = deleteNode.delete(key, internalFlag)
        # newRoot의 값이 None이 아닌 경우 루트가 새롭게 바뀌었다는 뜻이므로 트리의 루트를 갱신한다.
        if newRoot:
            self.root = newRoot

    def print_tree(self, node, level):
        indent = "  " * level
        if node.isLeaf:
            print(f"{indent}LeafNode(keys={node.keys}, values={[v.strip('\'"').strip("'") for v in node.values]})")
            if node.r:
                print(f"{indent} -> Right sibling: LeafNode(keys={node.r.keys})")
        else:
            print(f"{indent}InternalNode(keys={node.keys})")
            for i, child in enumerate(node.children):
                print(f"{indent}  Child {i}:")
                self.print_tree(child, level + 1)  # 자식 노드를 재귀적으로 출력

            # Rightmost child 출력
            if node.r:
                print(f"{indent}  Rightmost Child:")
                self.print_tree(node.r, level + 1)

    def save_to_file(self, file_name, append = False):
        mode = 'a' if append else 'w' # 처음에 트리 생성 시 쓰여진 노드 크기(b) 값을 유지하기 위해 해당 로직 추가
        with open(file_name, mode) as f:
            self._save_tree_recursive(self.root, f)

    def _save_tree_recursive(self, node, file):
        if node.isLeaf:
            # right sibling이 있을 경우 그 ID를 기록, 없으면 'None' 기록
            right_sibling_id = 'None' if node.r is None else node.r.id
            file.write(f"LeafNode {node.id} {node.keys};{node.values};{right_sibling_id}\n")
        else:
            # internal node의 자식 ID를 기록
            children_ids = [child.id for child in node.children]
            right_sibling_id = 'None' if node.r is None else node.r.id
            file.write(f"InternalNode {node.id} {node.keys};{children_ids};{right_sibling_id}\n")

            # 자식 노드들에 대해 재귀 호출하여 기록
            for child in node.children:
                self._save_tree_recursive(child, file)

            # 마지막 자식의 rightmost sibling도 기록
            if node.r:
                self._save_tree_recursive(node.r, file)

    def load_from_file(self, file_name):
        with open(file_name, 'r') as f:
            lines = f.readlines()

        # 첫 번째 줄에서 노드 크기(b)를 가져옴
        self.b = int(lines[0].strip())

        # 노드 ID에 따라 노드를 저장하는 맵
        node_map = {}

        # 첫 번째 줄 이후부터 노드 정보를 처리
        for line in lines[1:]:
            parts = line.strip().split(';')
            
            # 노드 타입과 나머지 정보를 분리
            node_type, keys_str = parts[0].split(' ', 1)

            # keys_str에서 노드 ID와 키들을 분리
            node_id_str, keys_list_str = keys_str.split(' ', 1)
            node_id = int(node_id_str)  # 노드 ID 추출
            keys = list(map(int, keys_list_str.strip('[]').split(','))) if keys_list_str.strip('[]') else []
            
            if node_type == "LeafNode":
                node = LeafNode(self.b)
                node.keys = keys
                # 실제 저장된 값을 복원
                values_str = parts[1].strip()
                node.values = values_str.strip('[]').split(', ') if values_str.strip('[]') else []
                node_map[node_id] = node  # 노드를 node_map에 저장

            # InternalNode의 경우
            elif node_type == "InternalNode":
                node = InternalNode(self.b)
                node.keys = keys
                node_map[node_id] = node  # 노드를 node_map에 저장

        # 자식 노드와 형제 노드를 설정
        for line in lines[1:]:
            parts = line.strip().split(';')
            # 노드 타입과 나머지 정보를 분리
            node_type, keys_str = parts[0].split(' ', 1)

            # keys_str에서 노드 ID와 키들을 분리
            node_id_str, keys_list_str = keys_str.split(' ', 1)
            node_id = int(node_id_str)  # 노드 ID 추출
            keys = list(map(int, keys_list_str.strip('[]').split(','))) if keys_list_str.strip('[]') else []
            
            node = node_map[node_id]  # ID를 사용해 현재 노드를 찾음

            if node_type == "LeafNode":
                right_sibling_id = parts[2].strip() if parts[2] != 'None' else None
                if right_sibling_id:
                    node.r = node_map.get(int(right_sibling_id), None)

            elif node_type == "InternalNode":
                children_ids = list(map(int, parts[1].strip('[]').split(','))) if parts[1].strip('[]') else []
                node.children = [node_map.get(child_id, None) for child_id in children_ids]

                right_sibling_id = parts[2].strip() if len(parts) > 2 and parts[2] != 'None' else None
                if right_sibling_id:
                    node.r = node_map.get(int(right_sibling_id), None)

        # 마지막으로 부모 노드와 자식 노드 관계를 설정
        for node in node_map.values():
            if isinstance(node, InternalNode):
                for child in node.children:
                    child.parent = node
                if node.r:
                    node.r.parent = node

        # 루트를 설정 (부모가 없는 노드를 루트로 간주)
        for node in node_map.values():
            if node.parent is None:
                self.root = node
                break

        return self



def main():
    parser = argparse.ArgumentParser(description="B+ Tree Command Line Interface")

    # index file creation 명령어
    parser.add_argument("-c", "--create", nargs=2, help="Create a new index file", metavar=("INDEX_FILE", "NODE_SIZE"))
    # insertion 명령어
    parser.add_argument("-i", "--insert", nargs=2, help="Insert data into the index", metavar=("INDEX_FILE", "DATA_FILE"))
    # search 명령어
    parser.add_argument("-s", "--search", nargs=2, help="Search a value of a pointer to a record with the key", metavar=("INDEX_FILE", "KEY"))
    # range search 명령어
    parser.add_argument("-r", "--range_search", nargs=3, help="Search the values of pointers to records having the keys within the range provided", metavar=("INDEX_FILE", "START_KEY", "END_KEY"))
    # deletion 명령어
    parser.add_argument("-d", "--delete", nargs=2, help="Delete all the key-value pairs inside the input data file from the idnex file", metavar=("INDEX_FILE", "DATA_FILE"))

    parser.add_argument("-p", "--print", nargs=1, help="Print index file tree structure", metavar=("INDEX_FILE"))
    args = parser.parse_args()

    # 전역 변수로 설정된 노드 크기 b
    node_size = None
    tree = None

    # 인덱스 파일 생성 명령
    if args.create:
        index_file = args.create[0]  # 인덱스 파일 이름
        node_size = int(args.create[1])  # 노드 크기 b
        tree = BPlusTree(node_size)  # 트리 생성
        print(f"Created a new B+ tree with node size: {node_size}")

        with open(index_file, 'w') as f:
            f.write(f"{node_size}\n")  # 인덱스 파일의 첫 번째 줄에 b 값 기록
        print(f"Index file {index_file} saved with initial tree structure.")

    # 데이터 삽입 명령
    elif args.insert:
        index_file = args.insert[0]
        data_file = args.insert[1]
        node_size = 0

        with open(index_file, 'r') as f:
            node_size = int(f.readline().strip())

        # 이거 고치기. 입력한 크기로 돼야 하는데 무조건 4로 됨.
        tree = BPlusTree(node_size)

        if tree is None:
            print("Empty Tree")
            return
        
        with open(data_file, 'r') as f:
            for line in f:
                key, value = line.strip().split(',')
                tree.insert(int(key), value)

        #tree.print_tree(tree.root, 0)
        tree.save_to_file(index_file, append = True)

    # search 명령
    elif args.search:
        global find_route
        global val
        index_file = args.search[0]
        search_key = int(args.search[1])

        tree = BPlusTree(0) # 우선 최대 노드 개수를 0으로 설정.
        tree = tree.load_from_file(index_file) # 인덱스 파일에 저장된 정보를 불러와 트리를 구성. 트리의 최대 노드 개수도 재설정 됨

        if tree is None:
            print("Empty Tree")
        
        if tree.search(search_key) is None:
            print("NOT FOUND")
            return
        
        for keys in find_route:
            print(keys)
        print(val)

    # range search 명령
    elif args.range_search:
        index_file = args.range_search[0]
        start_key = int(args.range_search[1])
        end_key = int(args.range_search[2])

        tree = BPlusTree(0) # 우선 최대 노드 개수를 0으로 설정.
        tree = tree.load_from_file(index_file) # 인덱스 파일에 저장된 정보를 불러와 트리를 구성. 트리의 최대 노드 개수도 재설정 됨

        if tree is None:
            print("Empty Tree")
            return
        
        tree.range_search(start_key, end_key)

    # deletion 명령
    elif args.delete:
        index_file = args.delete[0]
        data_file = args.delete[1]

        keys = [] # 지워야 할 노드들의 키를 담는 배열
        with open(data_file, 'r') as f:
            for line in f:
                keys.append(int(line))

        tree = BPlusTree(0) # 우선 최대 노드 개수를 0으로 설정
        tree = tree.load_from_file(index_file) # 인덱스 파일에 저장된 정보를 불러와 트리를 구성. 트리의 최대 노드 개수도 재설정 됨

        if tree is None:
            print("Empty Tree")
            return
        
        for key in keys:
            tree.delete(key)

        # index file에 변경된 트리를 반영한다.
        # index file의 첫 번째 줄에 노드 사이즈를 남긴다.
        node_size = 0
        with open(index_file, 'r') as f:
            node_size = int(f.readline().strip())
        with open(index_file, 'w') as f:
            f.write(str(node_size))
            f.write('\n')
        # 두 번째 줄부터 새롭게 바뀐 트리를 반영한다.
        tree.save_to_file(index_file, append=True)

    elif args.print:
        index_file = args.print[0]

        tree = BPlusTree(0)
        tree = tree.load_from_file(index_file)
        tree.print_tree(tree.root, 0)

if __name__ == "__main__":
    main()


'''
남은 할 일
1. 예외처리 (없는 키 삭제하려 하면 에러 나는거 고치기)
2. 출력 형식 과제 명세에 맞추기
3. 최적화
4. 위키 쓰기
'''