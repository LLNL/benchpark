import ramble.config as cfg
import spack.util.spack_yaml as syaml
import sys

def main():
    """This ramble-python script can be used to merge two
    ramble YAML configs with overlapping sections into
    a single config file.
    """
    f1, f2, output = sys.argv[1], sys.argv[2], sys.argv[3]

    c1 = cfg.read_config_file(f1)
    c2 = cfg.read_config_file(f2)

    cfg.merge_yaml(c1, c2)
    with open(output, "w") as outstream:
        syaml.dump_config(c1, outstream)

if __name__ == "__main__":
    main()
