from datetime import datetime, timedelta
import os
import shutil
import sys


class Update:
    def __init__(self) -> None:
        # Verify that the chromedriver zip is in the directory
        zip_file = "chromedriver_mac64_m1.zip"
        if not os.path.exists(zip_file):
            sys.exit(
                "Looks like the chromedriver updatefile isn't in our directory. Exiting. . ."
            )
        else:
            shutil.unpack_archive(zip_file, ".")
            os.system("chmod +x chromedriver")
            print("\nPlease enter your MacBook password, then press Enter to continue")
            print(
                "NOTE: The white cursor will not display your password while typing, this is normal"
            )
            os.system("sudo mv chromedriver /usr/local/bin")
            if os.path.exists("/usr/local/bin/chromedriver"):
                time_modified = os.path.getmtime("/usr/local/bin/chromedriver")
                if datetime.fromtimestamp(time_modified) >= datetime.now() - timedelta(
                    hours=1
                ):
                    print("Successfully updated chromedriver!")
                    print("continuing AmexRec Script\n")
                    os.system("rm chromedriver_mac64_m1.zip")
                else:
                    sys.exit(
                        "Couldn't update chromedriver for some reason, exiting. . ."
                    )
            else:
                sys.exit("Chromedriver seems to be missing, exiting. . .")
