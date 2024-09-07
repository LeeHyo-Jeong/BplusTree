import argparse

class Node:
    # 클래스 내에서 전역적으로 사용되는 카운터
    # 노드가 몇 개 생성되었는지를 나타낸다.
    _id_counter = 0

    def __init__(self, b):
        self.id = Node._get_next_id()
        self.m = 0           # key의 개수
        self.keys = []       # key들의 배열, 오름차순으로 정렬되어 있다. p를 keys와 (children 또는 values)로 나누어서 구현한다.
        self.isLeaf = False  # 이 노드가 leaf node인지를 판단하는 boolean
        self.b = b
        self.maxKeys = b - 1 # 노드가 가질 수 있는 최대 키의 개수 (b - 1과 동일)
        self.parent = None   # 부모 노드에 대한 포인터

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
        findNode = self.root
        if findNode is None:
            return None
        
        # leaf까지 내려간다.
        while findNode is not None and not findNode.isLeaf:
            print(str(findNode.keys).strip('[]'))
            # 타고 내려갈 적절한 child node를 찾는다.
            childIdx = 0
            while childIdx < len(findNode.keys) and key >= findNode.keys[childIdx]:
                childIdx += 1

            # rightmost child도 비교한다.
            # 모든 left children들의 키들보다 찾으려는 키가 큰 경우 rightmost child로 내려간다.
            if childIdx == len(findNode.keys) and findNode.r:
                findNode = findNode.r
            else:
                findNode = findNode.children[childIdx]
        
        # 도달한 leaf node 안에서 해당 키가 존재하는지 찾는다.
        keyIdx = 0
        while keyIdx < len(findNode.keys):
            if findNode.keys[keyIdx] == key:
                # 트리 안에 키가 존재하는 경우 그 키에 대응하는 값을 리턴
                return findNode.values[keyIdx]
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
                    print(f"{findNode.keys[idx]}, {findNode.values[idx]}")
                idx += 1
            findNode = findNode.r

    def print_tree(self, node, level):
        indent = "  " * level
        if node.isLeaf:
            print(f"{indent}LeafNode(keys={node.keys}, values={node.values})")
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
            file.write(f"LeafNode {node.keys};{right_sibling_id}\n")
        else:
            # internal node의 자식 ID를 기록
            children_ids = [child.id for child in node.children]
            right_sibling_id = 'None' if node.r is None else node.r.id
            file.write(f"InternalNode {node.keys};{children_ids};{right_sibling_id}\n")

            # 자식 노드들에 대해 재귀 호출하여 기록
            for child in node.children:
                self._save_tree_recursive(child, file)

            # 마지막 자식의 rightmost sibling도 기록
            if node.r:
                self._save_tree_recursive(node.r, file)

    def load_from_file(self, file_name):
        pass
    
'''
    def load_from_file(self, file_name):
        node_map = {}
        with open(file_name, 'r') as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(';')
                node_type, keys = parts[0].split(' ', 1)
                keys = list(map(int, keys.strip('[]').split(','))) if keys.strip('[]') else []

                # 오른쪽 형제 노드 ID 파싱
                right_sibling_id = parts[1].strip() if parts[1] != 'None' else None

                if node_type == "LeafNode":
                    node = LeafNode(self.b)
                    node.keys = keys
                    node.values = ['placeholder'] * len(keys)  # 임시 값으로 설정
                    node_map[node.id] = node  # 노드를 저장
                else:
                    node = InternalNode(self.b)
                    node.keys = keys
                    node_map[node.id] = node  # 노드를 저장

                # 오른쪽 형제 노드 복원 처리
                if right_sibling_id and right_sibling_id != 'None':
                    try:
                        node.r = node_map.get(int(right_sibling_id))  # 하나의 형제 노드만 처리
                    except ValueError:
                        print(f"잘못된 형제 노드 ID: {right_sibling_id}")
                        node.r = None
                else:
                    node.r = None

            # InternalNode의 자식 복원 처리
            for line in lines:
                parts = line.strip().split(';')
                node_type, keys = parts[0].split(' ', 1)
                keys = list(map(int, keys.strip('[]').split(','))) if keys.strip('[]') else []
                if node_type == "InternalNode":
                    children_ids = list(map(int, parts[2].strip('[]').split(','))) if len(parts) > 2 else []
                    node = node_map[node.id]
                    node.children = [node_map[child_id] for child_id in children_ids]

        # 루트 설정: 부모가 없는 노드를 루트로 설정
        for node_id in node_map:
            node = node_map[node_id]
            if node.parent is None:
                self.root = node
                break


'''

def main():
    parser = argparse.ArgumentParser(description="B+ Tree Command Line Interface")

    # 인덱스 파일 생성 명령어
    parser.add_argument("-c", "--create", nargs=2, help="Create a new index file", metavar=("INDEX_FILE", "NODE_SIZE"))
    # 데이터 삽입 명령어
    parser.add_argument("-i", "--insert", nargs=2, help="Insert data into the index", metavar=("INDEX_FILE", "DATA_FILE"))
    # search 명령어
    parser.add_argument("-s", "--search", nargs=2, help="Search a value of a pointer to a record with the key", metavar=("INDEX_FILE", "KEY"))
    # range search 명령어
    parser.add_argument("-r", "--range_search", nargs=3, help="Search the values of pointers to records having the keys within the range provided", metavar=("INDEX_FILE", "START_KEY", "END_KEY"))

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
        tree.save_to_file(index_file, append = True)  # 최초 트리 구조를 파일에 저장

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
                if int(key) == 70:
                    print("here")
                tree.insert(int(key), value)

        tree.print_tree(tree.root, 0)
        tree.save_to_file(index_file, append = True)

    # search 명령
    elif args.search:
        index_file = args.search[0]
        search_key = int(args.search[1])
        node_size = 0

        with open(index_file, 'r') as f:
            node_size = int(f.readline().strip())

        tree = BPlusTree(node_size)  # 기본적으로 node size는 4로 설정, 인덱스 파일을 통해 복원 가능
        print("***")
        print(tree.b)

        # load_from_file 고치고 이 부분 load_from_file로 얻어온 트리에서 서치하는거로 바꿔야함.
        data_file="testInput.csv"
        with open(data_file, 'r') as f:
            for line in f:
                key, value = line.strip().split(',')
                tree.insert(int(key), value)

        # tree.print_tree(tree.root, 0)

        if tree is None:
            print("Empty Tree")
            return

        result = tree.search(search_key)
        if result is not None:
            print(result)
        else:
            print("NOT FOUND")

    # range search 명령
    elif args.range_search:
        index_file = args.range_search[0]
        start_key = int(args.range_search[1])
        end_key = int(args.range_search[2])

        tree = BPlusTree(4)  # 기본 크기 4로 설정
        tree.load_from_file(index_file)  # index.dat 파일에서 트리를 복원

        # load_from_file 고치고 이 부분 load_from_file로 얻어온 트리에서 서치하는거로 바꿔야함.
        data_file="testInput.csv"
        with open(data_file, 'r') as f:
            for line in f:
                key, value = line.strip().split(',')
                tree.insert(int(key), value)

        if tree is None:
            print("Empty Tree")
            return
            

        tree.range_search(start_key, end_key)



if __name__ == "__main__":
    main()
