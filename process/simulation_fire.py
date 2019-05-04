import numpy as np
from scipy import signal
import pandas as pd

class SimulationFire():
	def __init__(self, map_top_left, map_bottom_right, grid_width, n_steps, \
		transfer_matrix, fire_starts=None, random_seed=0):
		# Set randomness
		np.random.seed(random_seed)


		# Geography
		self.map_top_left=map_top_left
		self.map_bottom_right=map_bottom_right
		self.grid = self._generate_grid(map_top_left, map_bottom_right, grid_width)    

		# Fire locations - TODO add fire_starts and create function
		if fire_starts is None:
			self.fire_starts = [(self.grid.shape[0]//2, self.grid.shape[1]//2)]

		self.fire_matrix_t0 = np.zeros((self.grid.shape[0], self.grid.shape[1]))
		for pos in self.fire_starts:
			self.fire_matrix_t0[pos[0], pos[1]]=1

		# Simulation parameters
		self.n_steps=n_steps

		# Fire propagation
		self.transfer_matrix = transfer_matrix



	def run(self):
		self.all_fires=self._fire_locations(self.fire_matrix_t0	, self.transfer_matrix)
		return self.all_fires


	def _grid_coordinates(self, lats, lons):
		"""
		Generates a 3-D array grid such that grid[i, j] = [lats[i], lons[j]]
		Inputs:
			lats: np.array of size (N,)
			lons: np.array of size (M,)
		Returns:
			grid: np.array of size (N,M,2)
		"""
		grid = np.zeros((len(lats), len(lons), 2))
		for idx_lat, lat in enumerate(lats):
			for idx_lon, lon in enumerate(lons):
				grid[idx_lat, idx_lon] = [lat, lon]
		return grid

	def _generate_grid(self, top_left, bottom_right, grid_width):
		latitudes = np.round(np.arange(start=top_left[0], stop=bottom_right[0]+1.5*grid_width, step=-grid_width),3)
		longitudes = np.round(np.arange(start=top_left[1], stop=bottom_right[1]+1.5*grid_width, step=grid_width),3)
		grid_coordinates = self._grid_coordinates(latitudes, longitudes)
		return grid_coordinates

	def _perturbation_matrix(self, matrix, variance=0.3):
		"""
		Random gaussian perturbation of mean 0 on a given matrix.
		Input:
			matrix: np.array like
			variance: float
		Returns:
			perturbation_matrix: np.array of same shape as matrix
		"""
		return matrix + variance*np.random.randn(*matrix.shape)

	def _fire_locations(self, initial_matrix, transfer_matrix, fire_threshold=0.8):
		"""
		Given an initial matrix with ones at the location of a fire, we run a simulation of how the fire
		will evolve given a transfer matrix which takes into account parameters such as wind direction.
		Input:
			initial_matrix: np.array
			transfer_matrix: np.array
		Return:
			fire_loc_df: pd.DataFrame. Contains all locations on fire for any given timepoint.
		"""
		fire_matrix = initial_matrix.copy()
		
		fire_loc_df = pd.DataFrame(columns=['latitude', 'longitude', 'time'])

		for t in range(self.n_steps):
			on_fire = self.grid[fire_matrix >= fire_threshold]
			time =  t*np.ones(len(on_fire)).reshape(-1,1)
			on_fire = pd.DataFrame(np.hstack((on_fire, time)), columns=['latitude', 'longitude', 'time'])

			fire_loc_df = fire_loc_df.append(on_fire)

			fire_matrix += signal.convolve(fire_matrix, self._perturbation_matrix(transfer_matrix), mode='same')

			# Setting values between 0 and 1
			fire_matrix = np.minimum(fire_matrix, 1)
			fire_matrix = np.maximum(fire_matrix, 0)

		return fire_loc_df



