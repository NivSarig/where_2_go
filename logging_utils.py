# from datetime import datetime
#
# DO_PRINT = False
# log_file_name = f'/home/niv/dev/route_your_way/log.log'
# COLOR_RED = "\033[91m"
# COLOR_GREEN = "\033[92m"
# COLOR_YELLOW = "\033[93m"
# COLOR_RESET = "\033[0m"  # Reset color to default
#
#
# def formatted_now(time_format='%Y:%m:%d-%H:%M:%S.%f'):
#     return datetime.now().strftime(time_format)
#
#
# def create_logger(log_file_name):
#     print(log_file_name)
#     open(log_file_name, 'w').close()
#
#     def log_func(msg, do_print=DO_PRINT, end="\n"):
#         if do_print:
#             print(msg, end=end)
#         with open(log_file_name, 'a+') as fid:
#             fid.write(f"{COLOR_RED}{formatted_now()}{COLOR_RESET}|{COLOR_GREEN}msg:{COLOR_RESET}{msg}\n")
#
#     return log_func
#
#
# log = create_logger(log_file_name)
# #
# # log(f"New run")
#
#
