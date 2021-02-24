# python subscribe.py
import subscribe_platform as sp

if __name__ == '__main__':
    subscribe_platform = sp.SubscribePlatform('172.16.10.2', client_name='SP')
    subscribe_platform.run()
    # subscribe_platform.unbind_device()
