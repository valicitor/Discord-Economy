class SimpleNoiseGenerator:
    """Lightweight noise generator without external dependencies"""
    
    @staticmethod
    def simple_noise_2d(x: float, y: float, seed: int = 42) -> float:
        xi = int(x * 57.1)
        yi = int(y * 71.3)
        
        h = (xi * 1664525 + yi * 1013904223 + seed) & 0xFFFFFFFF
        h = (h ^ (h >> 16)) * 0x85EBCA77
        h = (h ^ (h >> 13)) * 0xC2B2AE35
        h = h ^ (h >> 16)
        
        return (h & 0x7FFFFFFF) / 0x7FFFFFFF
    
    @staticmethod
    def smooth_noise(x: float, y: float, seed: int = 42) -> float:
        xi = int(x)
        yi = int(y)
        fx = x - xi
        fy = y - yi
        
        v00 = SimpleNoiseGenerator.simple_noise_2d(xi, yi, seed)
        v10 = SimpleNoiseGenerator.simple_noise_2d(xi + 1, yi, seed)
        v01 = SimpleNoiseGenerator.simple_noise_2d(xi, yi + 1, seed)
        v11 = SimpleNoiseGenerator.simple_noise_2d(xi + 1, yi + 1, seed)
        
        fx = fx * fx * (3 - 2 * fx)
        fy = fy * fy * (3 - 2 * fy)
        
        v0 = v00 * (1 - fx) + v10 * fx
        v1 = v01 * (1 - fx) + v11 * fx
        
        return v0 * (1 - fy) + v1 * fy
    
    @staticmethod
    def fractal_noise(x: float, y: float, octaves: int = 3, 
                      persistence: float = 0.5, lacunarity: float = 2.0,
                      seed: int = 42) -> float:
        value = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            value += SimpleNoiseGenerator.smooth_noise(
                x * frequency, y * frequency, seed
            ) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        return value / max_value
