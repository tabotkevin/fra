from cryptography.fernet import Fernet

key = 'TluxwB3fV_GWuLkR1_BzGs1Zk90TYAuhNMZP_0q4WyM='

# Oh no! The code is going over the edge! What are you going to do?
message = b'gAAAAABc1gFny0pa3NM0SN84dlRpX5jx5SX96Lqu-YhjGPxyKe3NIo53kOAEF0AN9XZZMzbSnAfuTpF506fI0ewH8uJSim9K8pP4xBbhX7o8DUJmn8jUlCrfb-xAPBlg2_Xe2E6hAUFqhQO0X1EbtQOjN3aEh1TK5tmTR4OXA8_QdcmxATKLJh52nJE9E4oLf200uRcBvBX2'

def main(message, key):
    f = Fernet(key)
    print(f.decrypt(message))


if __name__ == "__main__":
    main(message, key)