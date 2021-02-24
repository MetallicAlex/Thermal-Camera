import publish_platform as pp
import subscribe_platform as sp
import multiprocessing


# mqtt.eclipse.org


def main():
    publish_platform = pp.PublishPlatform('172.16.10.2')
    publish_platform.set_device('7101239214001')
    publish_platform.find_token()
    #publish_platform.unbind_device()
    publish_platform.run()


if __name__ == "__main__":
    main()
