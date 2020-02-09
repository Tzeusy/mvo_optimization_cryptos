from typing import List

import numpy as np
import cvxopt as opt
from cvxopt import solvers
solvers.options['show_progress'] = False

def random_weight_generator(n:int) -> List[int]:
    """
    Arguments: Number of weights to generate
    
    Returns: List of weights that sum to 1
    """
    weights = np.random.rand(n)
    return weights / sum(weights)

def generate_random_portfolio_stats(ret_df):
    """Generates one random portfolio's returns and stddev
    
    Arguments:
        ret_df {pd.DataFrame} -- Returns DataFrame for which to generate a portfolio
    
    Returns:
        (float, float) -- Returns and Standard Deviation of randomly-weighted portfolio
    """    
    mean_ret = np.asmatrix(ret_df.mean())
    wt = np.asmatrix(random_weight_generator(ret_df.shape[1]))
    cov = ret_df.cov().to_numpy()
    mean_port_ret = wt * mean_ret.T
    stddev = np.sqrt(wt * cov * wt.T)
    return mean_port_ret, stddev

def optimal_weight_vector(ret_df, cryptocurrencies):
    """Creates optimal weight vector
    
    Arguments:
        ret_df {DataFrame} -- Returns DataFrame
        cryptocurrencies {List[str]} -- List of cryptocurrencies
    
    Returns:
        port_weights {dict} -- Weights for portfolios
        port_returns {List} -- List of returns for optimal portfolios
        port_stdvs {List} -- Accompanying list of stdvs for optimal portfolios
        return_weight_mapping {dict} -- Weights of cryptocurrencies
    """     
    cov = np.matrix(ret_df.cov())
    n = ret_df.shape[1]
    avg_ret = np.matrix(ret_df.mean()).T
    r_min = 0.05
    mus = []
    for i in range(100):  # Generate array of targets
        r_min += 0.0005
        mus.append(r_min)
    P = opt.matrix(cov)
    q = opt.matrix(np.zeros((n, 1)))
    G = opt.matrix(np.concatenate((
                -np.transpose(np.array(avg_ret)), 
                -np.identity(n)), 0))
    A = opt.matrix(1.0, (1,n))
    b = opt.matrix(1.0)
    port_weights = [
        solvers.qp(
            P, q, G, 
            opt.matrix(
                np.concatenate((-np.ones((1,1))*yy, np.zeros((n,1))), 0)
            ),
            A, b
        )['x'] for yy in mus
    ]
    port_returns = [(np.matrix(x).T * avg_ret)[0,0] for x in port_weights]
    port_stdvs = [np.sqrt(np.matrix(x).T * cov.T.dot(np.matrix(x)))[0,0] for x in port_weights]
    return_weight_mapping = {
        mus[i]: {
            cryptocurrencies[j]:f'{weight:,.3f}'
            for j, weight in enumerate (list(port_weights[i]))
        } for i in range(100)
    }
    return_weight_mapping = [
        {
            'Target':f'{mus[i]:,.4f}',
            'Weights': {
                cryptocurrencies[j]:f'{weight:,.3f}'
                for j, weight in enumerate (list(port_weights[i]))
            }
        } for i in range(100)
    ]
    return port_weights, port_returns, port_stdvs, return_weight_mapping