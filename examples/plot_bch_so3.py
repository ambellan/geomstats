"""
Visualize the first, second and third order approximation of the Baker Campbell
Hausdorf formula on so(n). To this end, sample 2 random elements a,b of so(n)
and compute both the BCH approximations of different orders as well as
log(exp(a)exp(b)) and compare these in the Frobenius norm.

Notice that the BCH only guarantees convergence if ||a|| + ||b|| < log 2,
so we normalize the random vectors to have norm 1 / 2.

We also compare execution times of the scikit-learn expm / logm implementation
with our BCH-implementation, for small orders approximation by BCH is faster
than the scikit-learn version, while being close to the actual value.

"""
import timeit

import matplotlib.pyplot as plt

import geomstats.backend as gs
from geomstats.geometry.skew_symmetric_matrices import SkewSymmetricMatrices
from geomstats.geometry.special_orthogonal_group import SpecialOrthogonalGroup


n = 3
max_order = 10

group = SpecialOrthogonalGroup(n=n)
group.default_point_type = "matrix"

dim = int(n * (n - 1) / 2)
algebra = SkewSymmetricMatrices(n=n)


def main():
    norm_rv_1 = gs.normal(size=dim)
    tan_rv_1 = algebra.matrix_representation(
        norm_rv_1 / gs.norm(norm_rv_1, axis=0) / 2
    )
    exp_1 = gs.linalg.expm(tan_rv_1)

    norm_rv_2 = gs.normal(size=dim)
    tan_rv_2 = algebra.matrix_representation(
        norm_rv_2 / gs.norm(norm_rv_2, axis=0) / 2
    )
    exp_2 = gs.linalg.expm(tan_rv_2)

    composition = group.compose(exp_1, exp_2)

    orders = gs.arange(1, max_order + 1)
    bch_approximations = gs.array(
        [
            algebra.baker_campbell_hausdorff(tan_rv_1, tan_rv_2, order=n)
            for n in orders
        ]
    )
    bch_approximations = algebra.basis_representation(bch_approximations)
    correct = algebra.basis_representation(gs.linalg.logm(composition))
    t_numpy = timeit.timeit(
        lambda: gs.linalg.logm(
            gs.matmul(gs.linalg.expm(tan_rv_1), gs.linalg.expm(tan_rv_2))
        ),
        number=100,
    )
    t_bch = [
        timeit.timeit(
            lambda: algebra.baker_campbell_hausdorff(
                tan_rv_1, tan_rv_2, order=n
            ),
            number=100,
        )
        for n in orders
    ]
    frobenius_error = gs.linalg.norm(bch_approximations - correct, axis=1)

    plt.subplot(2, 1, 1)
    plt.scatter(orders, frobenius_error)
    plt.xlabel("Order of approximation")
    plt.ylabel("Error in Frob. norm")
    plt.grid()

    plt.subplot(2, 1, 2)
    plt.scatter(orders, t_bch)
    plt.hlines(y=t_numpy, xmin=1, xmax=max_order)
    plt.xlabel("Order of approximation")
    plt.ylabel("Execution time[s] for 100 replications vs. numpy")
    plt.grid()

    plt.show()
    plt.close()


if __name__ == "__main__":
    main()
