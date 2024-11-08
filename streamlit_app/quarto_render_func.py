# Modified from https://github.com/quarto-dev/quarto-python/tree/main to allow additional params
# and add in additional logging

import os
import sys
import shutil
import subprocess
import yaml
import tempfile

def path():
  path_env = os.getenv("QUARTO_PATH")
  if path_env is None:
    print("QUARTO_PATH variable not set")
    result = shutil.which("quarto")
    print(f'shutil.which("quarto") returned {result}')
    return result
  else:
    print(f"QUARTO_PATH env variable is {path_env}")
    return path_env

def find_quarto():
  quarto = path()
  if quarto is None:
    raise FileNotFoundError('Unable to find quarto command line tools.')
  else:
    print(f"Quarto successfully found at {quarto}")
    return quarto

def render_quarto(
    input,
    output_format = None,
    output_file = None,
    output_dir = None,
    execute = None,
    params = None,
    execute_params = None,
    remove_params_file=False,
    execute_dir = None,
    cache = None,
    cache_refresh = False,
    kernel_keepalive = None,
    kernel_restart = False,
    debug = False,
    quiet = False,
    pandoc_args = None,
    print_command=False,
    verbose=True,
    find_quarto_path=False,
    **kwargs
    ):

  # params file to remove after render (if option enabled)
  params_file = None

  # build args
  args = ["render", input]

  if verbose:
    args.extend(["--verbose"])

  if output_format is not None:
    args.extend(["--to", output_format])

  if output_dir is not None:
    args.extend(["--output-dir", output_dir])

  if output_file is not None:
    args.extend(["--output", output_file])

  if execute is not None:
    if execute is True:
      args.append("--execute")
    elif execute is False:
      args.append("--no-execute")

  if execute_params is not None:
    params_file = tempfile.NamedTemporaryFile(mode = 'w',
                                              prefix="quarto-params",
                                              suffix=".yml",
                                              delete=False)
    yaml.dump(execute_params, params_file)
    params_file.close()
    args.extend(["--execute-params", params_file.name])

  if execute_dir is not None:
    args.extend(["--execute-dir", execute_dir])

  if cache is not None:
    if cache is True:
      args.append("--cache")
    elif cache is False:
      args.append("--no-cache")

  if cache_refresh is True:
    args.append("--cache-refresh")

  if kernel_keepalive is not None:
    args.extend(["--kernel-keepalive", str(kernel_keepalive)])

  if kernel_restart is True:
    args.append("--kernel-restart")

  if debug is True:
    args.append("--debug")

  if quiet is True:
    args.append("--quiet")

  if params is not None:
    for param in params:
      for key, value in param.items():
        param = key
        param_value = value
      if isinstance(param_value, str):
        args.append(f'-P {param}:"{param_value}"')
      else:
        args.append(f'-P {param}:{param_value}')

  # run process
  try:
    if find_quarto_path:
      print("Looking for Quarto")
      find_quarto_output = find_quarto()
      final_command = [find_quarto_output] + args
      if print_command:
        print(f"Final command: {' '.join(final_command)}")
      subprocess.run(final_command, **kwargs)
    else:
      final_command = ["quarto"] + args
      if print_command:
        print(f"Final command: {' '.join(final_command)}")
      subprocess.run(' '.join(final_command), **kwargs)
  finally:
    if params_file is not None and remove_params_file:
      os.remove(params_file.name)
