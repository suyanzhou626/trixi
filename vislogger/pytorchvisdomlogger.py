import numpy as np
import torch
from torch.autograd import Variable

from vislogger import NumpyVisdomLogger


class PytorchVisdomLogger(NumpyVisdomLogger):
    """
    Visual logger, inherits the NumpyVisdomLogger and plots/ logs pytorch tensors and variables on a Visdom server.
    """

    def process_params(self, f, *args, **kwargs):
        """
        Inherited "decorator": convert Pytorch variables and Tensors to numpy arrays
        """

        ### convert args
        args = (a.cpu().numpy() if type(a).__module__ == 'torch' else a for a in args)
        args = (a.data.cpu().numpy() if isinstance(a, Variable) else a for a in args)

        ### convert kwargs
        for key, data in kwargs.items():
            if isinstance(data, Variable):
                kwargs[key] = data.data.cpu().numpy()
            elif type(data).__module__ == 'torch':
                kwargs[key] = data.cpu().numpy()

        return f(self, *args, **kwargs)

    def plot_model_statistics(self, model, env_app=None, model_name="", plot_grad=False):
        """
        Plots statstics (mean, std, abs(max)) of the weights or the corresponding gradients of a model as a barplot

        :param model: Model with the weights
        :param env_app: visdom environment name appendix, if none is given, it uses "-histogram"
        :param model_name: Name of the model (is used as window name)
        :param plot_grad: If false plots weight statistics, if true plot the gradients of the weights
        """

        if env_app is None:
            env_app = "-histogram"

        means = []
        stds = []
        maxmin = []
        legendary = []
        for i, (m_param_name, m_param) in enumerate(model.named_parameters()):
            win_name = "%s_params" % model_name
            if plot_grad:
                m_param = m_param.grad
                win_name = "%s_grad" % model_name

            param_mean = m_param.data.mean()
            param_std = np.sqrt(m_param.data.var())

            means.append(param_mean)
            stds.append(param_std)
            maxmin.append(torch.max(torch.abs(m_param)).data[0])
            legendary.append("%s-%s" % (model_name, m_param_name))

        self.show_barplot(name=win_name, array=np.asarray([means, stds, maxmin]), legend=legendary,
                          rownames=["mean", "std", "max"], env_app=env_app)

    def plot_model_statistics_weights(self, model, env_app=None, model_name=""):
        """
        Plots statstics (mean, std, abs(max)) of the weights of a model as a barplot (uses plot model statistics with
        plot_grad=False  )

        :param model: Model with the weights
        :param env_app: visdom environment name appendix, if none is given, it uses "-histogram"
        :param model_name: Name of the model (is used as window name)
        """
        self.plot_model_statistics(model=model, env_app=env_app, model_name=model_name, plot_grad=False)

    def plot_model_statistics_grads(self, model, env_app=None, model_name=""):
        """
        Plots statstics (mean, std, abs(max)) of the gradients of a model as a barplot (uses plot model statistics with
        plot_grad=True )

        :param model: Model with the weights and the corresponding gradients (have to calculated previously)
        :param env_app: visdom environment name appendix, if none is given, it uses "-histogram"
        :param model_name: Name of the model (is used as window name)
        """
        self.plot_model_statistics(model=model, env_app=env_app, model_name=model_name, plot_grad=True)

    def plot_mutliple_models_statistics_weights(self, model_dict, env_app=None):
        """
        Given models in a dict, plots the weight statistics of the models.

        :param model_dict: Dict with models, the key is assumed to be the name, while the value is the model
        :param env_app: visdom environment name appendix, if none is given, it uses "-histogram"
        """
        for model_name, model in model_dict.items():
            self.plot_model_statistics_weights(model=model, env_app=env_app, model_name=model_name)

    def plot_mutliple_models_statistics_grads(self, model_dict, env_app=None):
        """
        Given models in a dict, plots the gradient statistics of the models.

        :param model_dict: Dict with models, the key is assumed to be the name, while the value is the model
        :param env_app: visdom environment name appendix, if none is given, it uses "-histogram"
        """
        for model_name, model in model_dict.items():
            self.plot_model_statistics_grads(model=model, env_app=env_app, model_name=model_name)
