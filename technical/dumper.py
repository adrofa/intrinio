import os
import pickle


class Dumper(object):

    def __init__(self, dumpPath):

        self.path = os.path.normpath(dumpPath)
        if Dumper.CheckPath(dumpPath):
            print('{}: path already exists.'.format(self.path))
        else:
            os.mkdir(self.path)

    def Save(self, obj, name):
        """ Create a dump (with pickle pkg) of a provided object. """

        path = self.NameToPath(name=name)

        if Dumper.CheckPath(path):
            raise Exception('{}: dump already exists.'.format(name))

        else:
            with open(path, 'wb') as f:
                pickle.dump(obj, f)

    def Load(self, name):
        """ Loads a pickle dump. """

        path = self.NameToPath(name=name)

        if Dumper.CheckPath(path):
            with open(path, 'rb') as file:
                obj = pickle.load(file)
            return obj

        else:
            raise Exception('{}: dump does not exist.'.format(name))

    def Replace(self, obj, name):
        """ Overwrites a dump (with pickle pkg) of a provided object. """

        path = self.NameToPath(name=name)

        if Dumper.CheckPath(path):
            with open(path, 'wb') as f:
                pickle.dump(obj, f)

        else:
            raise Exception('{}: dump does not exist.'.format(name))

    def NameToPath(self, name):
        """ Adds '.pkl' to name and returns path. """

        pkl = name + '.pkl'
        path = os.path.join(self.path, pkl)
        return path

    @staticmethod
    def CheckPath(path):
        """ Checks if the provided path (dir / file) exists. """

        res = os.path.exists(path)
        return res
