import torch

class GPUAllocator(object):
    def __init__(self):

        """
        Usage:

        g = GPUAllocator()
        gpu_id = g.get_gpu()

        ## do something with gpu_id 

        g.set_as_free(gpu_id)

        """
        self.num_gpus = torch.cuda.device_count()
        self.gpu_names =  []

        for i in range(self.num_gpus):
            self.gpu_names.append('cuda:' +  str(i))

        self.usage = {}

        for i in range(self.num_gpus):
            self.usage[i] = False

        """
        on a good day, this is how the variables look like: 

        self.num_gpus= 2

        self.gpu_names= [
            'cuda:0', 
            'cuda:1'
        ]

        self.usage= {
            0: False,
            1: False
        }
        
        """


        print('Initiated GPU allocator with: ', self.gpu_names)

        """
        False: free 
        True: occupied 
        """

    def set_as_occupied(self, name: str):
        """
        True: occupied 
        """
        index = self.gpu_names.index(name)
        self.usage[index]= True

    def set_as_free(self, name: str):
        """
        False: free 
        """
        index = self.gpu_names.index(name)
        self.usage[index]= False


    def get_gpu(self):

        usage_values = list(self.usage.values())

        if False not in list(usage_values):
            return None
        else:
            for i in range(len(usage_values)):
                if usage_values[i] == False:
                    
                    gpu_name = self.gpu_names[i]
                    self.set_as_occupied(name = gpu_name)

                    return gpu_name

    def get_usage(self):
        d = {}
        usage_values = list(self.usage.values())
        for i in range(len(usage_values)):
            d[self.gpu_names[i]] = usage_values[i]

        return d