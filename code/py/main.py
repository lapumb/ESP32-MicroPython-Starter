# This file is executed on every boot (including wake-boot from deepsleep) AFTER boot.py (if applicable)

async def __print_heap_usage_task() -> None:
    import components.utils.utils as utils, uasyncio

    # print heap usage every five seconds
    while True:
        utils.print_heap_usage()
        await uasyncio.sleep_ms(5000)

def main() -> None:
    import uasyncio, aws_client_manager

    main_loop = uasyncio.get_event_loop()

    aws_client_manager.init("thing_name", "host_name", "aws_config/cert_file_path", "aws_config/private_key_file_path")
    uasyncio.create_task(__print_heap_usage_task())

    try:
        main_loop.run_forever()
    finally:
        main_loop.close()

if __name__ == "__main__":
    print("Running main.py..")

    try:
        main()
    except KeyboardInterrupt:
        print("Killing main.py..")
        import sys
        sys.exit(0)