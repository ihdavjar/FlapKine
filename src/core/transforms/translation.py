import numpy as np

class Translation_Transform:
    def __call__(self, input_, position):
        raise NotImplementedError("Each transform must implement the __call__ method.")

class ConstantT(Translation_Transform):
    def __call__(self, input_, position):
        return input_

class Translation_COM(Translation_Transform):

    def __call__(self, input_, position):
        # input: np.array of shape (n, 3) i.e (x, y, z)
        # position: np.array of shape (3,) i.e (x, y, z) at time t
        # output: np.array of shape (n, 3) i.e (x, y, z) at time t
        
        input_ = np.array(input_).reshape(-1, 3)
        position = np.array(position).reshape(3)

        assert input_.shape[1] == 3, "Input must have shape (n, 3)"
        assert position.shape[0] == 3, "Position must have shape (3,)"
        
        return input_ + position