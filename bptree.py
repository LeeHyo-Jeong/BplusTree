global b # 노드가 가질 수 있는 최대 자식의 개수

class Node:
    def __init__(self):
        self.m = 0          # key의 개수
        self.keys = []      # key들의 배열, 오름차순으로 정렬되어 있다. p를 keys와 (children 또는 values)로 나누어서 구현한다.
        self.isLeaf = False # 이 노드가 leaf node인지를 판단하는 boolean
        self.maxKeys = 0

    def isFull(self):
        # 노드가 꽉 찼는지 확인
        return self.m >= self.maxKeys

class InternalNode(Node):
    def __init__(self):
        super().__init__()
        self.children = []  # children[i]는 keys[i]의 left child를 가리키는 포인터, keys[i]는 child[i]와 child[i+1] 사이에 위치한다.
        self.r = None       # rightmost child node를 가리키는 포인터
        self.isLeaf = False

    def insert(self, key, child):
        # 노드 내의 키를 오름차순으로 유지하기 위해 삽입 할 적절한 위치를 찾는다.
        idx = 0
        while idx < len(self.keys) and idx < self.keys[i]:
            idx += 1

        self.keys.insert(idx, key) # 키 삽입
        self.children.insert(idx + 1, child) # 해당 키의 오른쪽 자식 노드 삽입

        if(len(self.keys) > self.maxKeys): # 노드가 꽉 찬 경우 분할
            return self.split() 

        # internal node에 있는 키들을 leaf node에 넣어야 하는데...? 고민을 해보자

    def split(self):
        midIdx = len(self.keys) // 2



class LeafNode(Node):
    def __init__(self):
        super().__init__()
        self.values = []    # values[i]는 keys[i]에 대응되는 값
        self.r = None       # right sibling을 가리키는 포인터
        self.isLeaf = True  