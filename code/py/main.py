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

    aws_client_manager.init("blakes_micropython_esp32_2", "a2thrw602myi6-ats.iot.us-east-1.amazonaws.com", "aws_config/cert.pem", "aws_config/private.key")
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