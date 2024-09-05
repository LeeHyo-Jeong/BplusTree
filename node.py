class Node:
    def __init__(self, b):
        self.m = 0           # key의 개수
        self.keys = []       # key들의 배열, 오름차순으로 정렬되어 있다. p를 keys와 (children 또는 values)로 나누어서 구현한다.
        self.isLeaf = False  # 이 노드가 leaf node인지를 판단하는 boolean
        self.b = b
        self.maxKeys = b - 1 # 노드가 가질 수 있는 최대 키의 개수 (b - 1과 동일)
        self.parent = None   # 부모 노드에 대한 포인터

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
        elif idx == len(self.keys) and self.r is not None and self.r.isLeaf:
            self.r.insert(key, value)
        else:
            if idx < len(self.children):
                self.children[idx].insert(key, value)
            elif idx == len(self.keys) and self.r is not None:
                self.r.insert(key, value)

        if len(self.keys) > self.maxKeys:
            self.split()


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
        self.r = None # 기존의 r은 제거

        # self.r은 어떻게 바꿔야 할지 고민좀....

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

            print(f"***Internal Node split function return: {newParentNode.keys}***")
            
            return newParentNode


        # 부모 노드가 존재한다면 부모 노드에 가운데 키 승천
        else:
            # 가운데 키가 부모 노드에서 들어갈 적절한 위치를 찾음
            idx = 0
            while idx < len(self.parent.keys) and midKey > self.parent.keys[idx]:
                idx += 1
    
            newRightNode.parent = self.parent # 분할된 오른쪽 노드의 부모 노드 지정
            self.parent.keys.insert(idx, midKey) # 가운데 키 부모 노드에 삽입
            self.parent.children.insert(idx + 1, newRightNode) # 오른쪽 분할 노드를 부모 노드의 새로운 자식으로 설정
            self.parent.m = len(self.parent.keys) # 부모 노드의 키 개수 업데이트

            if idx == len(self.parent.keys): # 부모 노드의 가장 마지막에 승천된 키가 삽입된다면 newRightNode는 부모 노드의 rightmost child가 된다.
                self.parent.r = newRightNode

            if len(self.parent.keys) == self.parent.maxKeys + 1:
                return self.parent.split()
            
            return None
            
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
        newRightNode.r = self.r
        newRightNode.m = len(newRightNode.keys)
        newRightNode.parent = self.parent # 여기 안되는듯. parent가 None으로 설정되어 있음. 애초부터 처음에 생성된 root의 parent가 설정 안 되어있음!! 그거 고치면 여기도 자동으로 될듯

        # 기존 노드에는 가운데 키와 값을 포함한 왼쪽 키와 값들만 남겨둔다.
        self.keys = self.keys[: midIdx + 1]
        self.values = self.values[: midIdx + 1]
        self.r = newRightNode
        self.m = len(self.keys)

        if self.parent is None:
            newParentNode = InternalNode(self.b) # 부모 노드는 leaf가 아닌 internal node
            newParentNode.keys = [midKey]
            newParentNode.children = [self, newRightNode]
            newParentNode.r = newRightNode
            newParentNode.m = 1
            self.parent = newParentNode
            newRightNode.parent = newParentNode

            return newParentNode

        else:
            # 부모 노드에 키를 삽입할 적절한 위치를 찾는다.
            idx = 0
            while idx < len(self.parent.keys) and midKey > self.parent.keys[idx]:
                idx += 1
            
            self.parent.keys.insert(idx, midKey)
            self.parent.children.insert(idx + 1, newRightNode)
            self.parent.m = len(self.parent.keys)

            newRightNode.parent = self.parent

            if idx == len(self.parent.keys): # 부모 노드의 가장 마지막에 승천된 키가 삽입된다면 newRightNode는 부모 노드의 rightmost child가 된다.
                self.parent.r = newRightNode

            if len(self.parent.keys) > self.parent.maxKeys:
                return self.parent.split()
            
        return None


import argparse

def print_tree(node, level=0):
    indent = "    " * level  # 들여쓰기 생성
    
    if node.isLeaf:
        print(f"{indent}LeafNode(keys={node.keys}, values={node.values})")
        if node.r:
            print(f"{indent}  -> Right sibling: LeafNode(keys={node.r.keys})")
    else:
        print(f"{indent}InternalNode(keys={node.keys})")
        for i, child in enumerate(node.children):
            print(f"{indent}  Child {i}:")
            print_tree(child, level + 1)  # 자식 노드를 재귀적으로 출력
        
        # Rightmost child 출력
        if node.r:
            print(f"{indent}  Rightmost Child:")
            print_tree(node.r, level + 1)



# 인덱스 파일을 생성하는 함수
def create_index_file(index_file, node_size):
    b = node_size  # b 값을 설정
    print(f"Index file {index_file} created with node size {b}")
    
    # 루트 노드를 LeafNode로 생성
    root = LeafNode(b)  # 처음에는 루트 노드를 LeafNode로 생성
    return root

# 데이터를 삽입하는 함수
def insert_into_tree(root, data_file):
    # CSV 파일에서 key-value를 읽어서 삽입
    with open(data_file, 'r') as f:
        for line in f:
            key, value = line.strip().split(',')
            key = int(key)

            # root 노드에 삽입 시도
            new_root = root.insert(key, value)  # 삽입 과정에서 분할 발생 시 새로운 루트 반환
            
            # 만약 새로운 루트가 반환되면, 트리의 루트를 갱신
            if new_root is not None:
                root = new_root  # 새로운 루트가 생긴 경우 갱신
                print(f"New root set: {root.keys}")


    while root.parent != None:
        root = root.parent
    print("Tree after insertion:")
    print_tree(root)



def main():
    parser = argparse.ArgumentParser(description="B+ Tree Command Line Interface")

    # 인덱스 파일 생성 명령어
    parser.add_argument("-c", "--create", nargs=2, help="Create a new index file", metavar=("INDEX_FILE", "NODE_SIZE"))
    # 데이터 삽입 명령어
    parser.add_argument("-i", "--insert", nargs=2, help="Insert data into the index", metavar=("INDEX_FILE", "DATA_FILE"))

    args = parser.parse_args()

    # 인덱스 파일 생성 명령
    if args.create:
        index_file = args.create[0]  # 인덱스 파일 이름
        node_size = int(args.create[1])  # 노드 크기 b
        root = create_index_file(index_file, node_size)  # 트리 생성
        print(f"Created a new B+ tree with node size: {node_size}")

    # 데이터 삽입 명령
    elif args.insert:
        index_file = args.insert[0]
        data_file = args.insert[1]
        root = create_index_file(index_file, 4)  # 임시로 node size 4 설정
        root = insert_into_tree(root, data_file)  # 최종 루트로 갱신


if __name__ == "__main__":
    main()
