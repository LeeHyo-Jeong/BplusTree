global b # 노드가 가질 수 있는 최대 자식의 개수

class Node:
    def __init__(self):
        global b

        self.m = 0           # key의 개수
        self.keys = []       # key들의 배열, 오름차순으로 정렬되어 있다. p를 keys와 (children 또는 values)로 나누어서 구현한다.
        self.isLeaf = False  # 이 노드가 leaf node인지를 판단하는 boolean
        self.maxKeys = b - 1 # 노드가 가질 수 있는 최대 키의 개수 (b - 1과 동일)
        self.parent = None   # 부모 노드에 대한 포인터

    def isFull(self):
        # 노드가 꽉 찼는지 확인
        return self.m >= self.maxKeys - 1

class InternalNode(Node):
    def __init__(self):
        super().__init__()
        self.children = []  # children[i]는 keys[i]의 left child를 가리키는 포인터, keys[i]는 child[i]와 child[i+1] 사이에 위치한다.
        self.r = None       # rightmost child node를 가리키는 포인터
        self.isLeaf = False

    def insert(self, key, child):
        # 노드 내의 키를 오름차순으로 유지하기 위해 삽입 할 적절한 위치를 찾는다.
        idx = 0
        while idx < len(self.keys) and key > self.keys[idx]:
            idx += 1

        self.keys.insert(idx, key) # 키 삽입
        self.children.insert(idx + 1, child) # 해당 키의 오른쪽 자식 노드 삽입
        child.parent = self

        if(len(self.keys) > self.maxKeys): # 노드가 꽉 찬 경우 분할
            return self.split() 

        self.m += 1 # 노드가 꽉 차지 않은 경우 분할이 일어나지 않으므로 key의 개수를 1 증가
        # internal node에 있는 키들을 leaf node에 넣어야 하는데...? 고민을 해보자

    def split(self):
        midIdx = len(self.keys) // 2
        midKey = self.keys[midIdx] # 가운데 키는 부모 노드로 승천
        
        # 가운데 키를 기준으로 노드를 좌우 분할
        # 새로운 노드로 기존 노드의 오른쪽 절반을 이동
        newRightNode = InternalNode()
        newRightNode.keys = self.keys[midIdx + 1 :] # 오른쪽 절반 키를 새로운 노드로 이동
        newRightNode.children = self.children[midIdx + 1 :] # 오른쪽 절반 키의 자식 노드도 새로운 노드로 이동
        newRightNode.m = len(newRightNode.keys) # 키의 개수 설정

        # 기존 노드에는 왼쪽 절반 정보만 남겨둠
        self.keys = self.keys[: midIdx] # 기존 노드에 왼쪽 절반 키만 남겨둠
        self.children = self.children[: midIdx + 1] # 기존 노드의 왼쪽 절반 키의 자식 노드만 남겨둠
        self.m = len(self.keys) # 키의 개수 설정


        # 분할된 노드들의 child들의 parent 포인터를 다시 설정
        for child in newRightNode.children:
            child.parent = newRightNode

        for child in self.children:
            child.parent = self
        
        # 부모 노드가 존재하지 않는다면 (루트인 경우) 새로운 부모 노드를 생성
        if self.parent is None:
            newParentNode = InternalNode()
            newParentNode.keys = [midKey]
            newParentNode.children = [self, newRightNode]
            newParentNode.m = 1 # 새롭게 만들어진 부모 노드에는 1개의 키만 존재하므로
            newParentNode.r = newRightNode
            self.parent = newParentNode # 새로운 부모 노드를 부모 포인터로 참조

        # 부모 노드가 존재한다면 부모 노드에 가운데 키 승천
        else:
            # 가운데 키가 부모 노드에서 들어갈 적절한 위치를 찾음
            idx = 0
            while idx < len(self.parent.keys) and midKey > self.parent.keys[idx]:
                idx += 1
    
            self.parent.keys.insert(idx, midKey) # 가운데 키 부모 노드에 삽입
            self.parent.children.insert(idx + 1, newRightNode) # 오른쪽 분할 노드를 부모 노드의 새로운 자식으로 설정
            self.parent.m = len(self.parent.keys) # 부모 노드의 키 개수 업데이트

            if idx == len(self.parent.keys): # 부모 노드의 가장 마지막에 승천된 키가 삽입된다면 newRightNode는 부모 노드의 rightmost child가 된다.
                self.parent.r = newRightNode

            

class LeafNode(Node):
    def __init__(self):
        super().__init__()
        self.values = []    # values[i]는 keys[i]에 대응되는 값
        self.r = None       # right sibling을 가리키는 포인터
        self.isLeaf = True  