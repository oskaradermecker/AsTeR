import numpy as np
import pandas as pd

class SimulationCalls():
	#NOTE: Use @autoassign in the future
	def __init__(self, map_center, map_radius, n_steps, \
		call_centers=None, background_call_centers=None, max_calls=250,\
		random_simulation=None, random_centers=10, random_seed=0):
		# Set randomness
		np.random.seed(random_seed)

		# Geography
		self.map_center=map_center
		self.map_radius=map_radius

		# Simulation parameters
		self.n_steps=n_steps
		self.max_calls=max_calls

		# Random similation / Debug mode
		self.random_simulation=random_simulation
		self.random_centers=random_centers

				
		if random_simulation:
			self.epicenters = epicenter_gen(map_center, map_radius, random_centers)
			self.background_epicenters = None
		else:
			self.epicenters = np.array([np.array(v) for (k,v) in call_centers.items()])
			self.background_epicenters = np.array([np.array(v) for (k,v) in background_call_centers.items()])

	def run(self):
		self.all_calls = self._all_calls_gen(self.epicenters, self.background_epicenters)
		return self.all_calls

	def _epicenter_gen(self, center, radius, nb_points):
		"""
		Draw random samples from a multivariate normal distribution with spherical covariance.
		Typical usage: generate specific approximate locations from which calls are coming.
		Input:
			center: distribution mean
			radius: distribution standard deviation
			nb_points: int. number of samples drawn
		Return:
			distribution: np.array
		"""
		return np.random.multivariate_normal(center, radius*np.identity(2), nb_points)

	def _calls_gen(self, centers, calls_per_center, radius=1e-5):
		"""
		Generates a set number of calls taken from a multivariate distribution around each center.
		Input:
			centers: np.array of size (n*2). Coordinates of centers.
			calls_per_center: np.array like of size n. Number of calls for each center.
		Return:
			all_calls: pd.DataFrame. Randomly generated calls.
		"""
		n=len(centers)
		all_calls = []
		for i in range(n):
			center_radius = np.random.normal(loc=radius, scale=radius/10)
			center_calls = self._epicenter_gen(centers[i,:], radius, calls_per_center[i])
			all_calls.append(center_calls)
		all_calls = np.concatenate(all_calls)
		all_calls = pd.DataFrame(all_calls, columns=['latitude', 'longitude'])
		
		all_calls['time'] = np.random.randint(low=0, high=self.n_steps, size=len(all_calls))
		
		return all_calls

	def _all_calls_gen(self, epicenters, background_epicenters=None):
		"""
		Generates a set number of calls taken from a multivariate distribution around each center.
		Input:
			centers: np.array of size (n*2). Coordinates of centers.
			calls_per_center: np.array like of size n. Number of calls for each center.
		Return:
			all_calls: pd.DataFrame. Randomly generated calls.
		"""
		nb_calls_epicenter = np.random.randint(low=1, high=self.max_calls, size=len(epicenters))
		all_calls = self._calls_gen(epicenters, nb_calls_epicenter)
		
		if not background_epicenters is None:
			nb_calls_epicenter = np.random.randint(low=5, high=self.max_calls, size=len(background_epicenters))
			background_calls = self._calls_gen(background_epicenters, nb_calls_epicenter, radius=1e-4)
			all_calls = pd.concat([all_calls, background_calls], axis=0)
			
		return all_calls
