import paramiko
import getpass
import sys

# --- Configuration ---
PORT = 22

# --- Keyboard Interactive Handler ---
def keyboard_interactive_handler(title, instructions, prompt_list):
    """
    Handles keyboard-interactive prompts.
    You might need to customize this based on the exact prompts your server sends.
    """
    print(f"--- Keyboard Interactive Auth ---")
    print(f"Title: {title}")
    print(f"Instructions: {instructions}")
    resp = []
    for prompt, _ in prompt_list:
        val = input(prompt + " ")
        resp.append(val)
    return resp

# --- SSH Connection and Operations ---
def ssh_connect(hostname: str, username: str):
    ssh_client = None
    try:
        # 1. Initialize SSH Client
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy())

        print(f"Connecting to {hostname}:{PORT} as {username}...")
        password = getpass.getpass(f"Enter password for {username}@{hostname}: ")

        try:
            ssh_client.connect(hostname=hostname,
                            port=PORT,
                            username=username,
                            password=password,
                            timeout=20,
                            allow_agent=False,
                            look_for_keys=False)

            transport = ssh_client.get_transport()
            if transport and transport.is_active() and not transport.is_authenticated():
                print("Password accepted, but further keyboard-interactive auth required.")
                try:
                    transport.auth_interactive(username, keyboard_interactive_handler)
                    if not transport.is_authenticated():
                        raise paramiko.AuthenticationException("Keyboard-interactive auth failed after password.")
                    print("Keyboard-interactive authentication successful.")
                except paramiko.AuthenticationException as auth_ex:
                    print(f"Authentication failed during interactive phase: {auth_ex}")
                    raise
                except Exception as e:
                    print(f"Error during interactive auth handling: {e}")
                    raise paramiko.SSHException(f"Error during interactive auth: {e}")

            elif not transport or not transport.is_active():
                raise paramiko.AuthenticationException("Connection failed or transport inactive after connect call.")


        except paramiko.AuthenticationException as e:
            print(f"Initial connection/authentication failed: {e}")
            try:
                transport = ssh_client.get_transport()
                if transport and 'keyboard-interactive' in transport.auth_handler.auth_methods_supported:
                    print("Password auth failed, trying keyboard-interactive from start...")
                    transport.auth_interactive(username, keyboard_interactive_handler)
                    if not transport.is_authenticated():
                        raise paramiko.AuthenticationException("Keyboard-interactive auth failed.")
                    print("Keyboard-interactive authentication successful.")
                else:
                    raise # Re-raise original exception if interactive not supported/tried
            except paramiko.AuthenticationException as ie:
                print(f"Keyboard-interactive authentication failed: {ie}")
                raise # Re-raise final exception
            except Exception as final_e:
                print(f"An unexpected error occurred during auth fallback: {final_e}")
                raise paramiko.SSHException(f"Unexpected auth error: {final_e}")

        print("Connection established successfully.")
    except paramiko.AuthenticationException as auth_fail:
        print(f"Authentication failed: {auth_fail}")
    except paramiko.SSHException as ssh_ex:
        print(f"Could not establish SSH connection or SSH protocol error: {ssh_ex}")
    except TimeoutError:
        print("Connection or command timed out.")
    except FileNotFoundError as fnf_ex:
        print(f"File not found during SFTP operation: {fnf_ex}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return ssh_client


def ssh_send_command(ssh_client: paramiko.SSHClient, command: str):
    print(f"\nExecuting command: '{command}'")
    try:
        _, stdout, stderr = ssh_client.exec_command(command, timeout=15)
        exit_status = stdout.channel.recv_exit_status()
        output = stdout.read().decode('utf-8')
        errors = stderr.read().decode('utf-8')
        print("\n--- Command Output ---")
        if output: print(output)
        if errors: print(f"--- Command Errors ---\n{errors}")
        print(f"--- Exit Status: {exit_status} ---")
    except paramiko.SSHException as ssh_ex:
        print(f"Could not establish SSH connection or SSH protocol error: {ssh_ex}")
    except TimeoutError:
        print("Connection or command timed out.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def ssh_send_file(ssh_client: paramiko.SSHClient, local_file_path: str, remote_file_path: str):
    try:
        print(f"\nCopying local file '{local_file_path}' to remote '{remote_file_path}'...")
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(local_file_path, remote_file_path)
        print("File copied successfully.")
    except paramiko.SSHException as ssh_ex:
        print(f"Could not establish SSH connection or SSH protocol error: {ssh_ex}")
    except TimeoutError:
        print("Connection or command timed out.")
    except FileNotFoundError as fnf_ex:
        print(f"File not found during SFTP operation: {fnf_ex}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def ssh_receive_file(ssh_client: paramiko.SSHClient, local_file_path: str, remote_file_path: str):
    try:
        print(f"\nCopying remote file '{remote_file_path}' to local '{local_file_path}'...")
        sftp_client = ssh_client.open_sftp()
        sftp_client.put(remote_file_path, local_file_path)
        print("File copied successfully.")
    except paramiko.SSHException as ssh_ex:
        print(f"Could not establish SSH connection or SSH protocol error: {ssh_ex}")
    except TimeoutError:
        print("Connection or command timed out.")
    except FileNotFoundError as fnf_ex:
        print(f"File not found during SFTP operation: {fnf_ex}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def ssh_close(ssh_client):
    if ssh_client:
        ssh_client.close()
        print("SSH connection closed.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} hostname username")
    username = sys.argv[2]
    hostname = sys.argv[1]
    ssh_client = ssh_connect(hostname, username)
    ssh_send_command(ssh_client, "ls -lah scratch")
    ssh_close(ssh_client)