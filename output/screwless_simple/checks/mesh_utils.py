"""Check actual saved binary STLs and 3MF documents, not the source geometry."""
from pathlib import Path
import json
import struct
import zipfile
import xml.etree.ElementTree as ET
import numpy as np
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
DTYPE = np.dtype([('normal', '<f4', 3), ('triangle', '<f4', (3, 3)), ('attribute', '<u2')])


def read_stl(path):
    data = path.read_bytes()
    count = struct.unpack_from('<I', data, 80)[0]
    assert len(data) == 84 + 50 * count, 'Unexpected binary STL length'
    return np.frombuffer(data, dtype=DTYPE, offset=84, count=count)['triangle'].astype(float)


def check_triangles(tris, exact_volume, expected_size):
    points, flat = np.unique(np.round(tris.reshape(-1, 3), 4), axis=0, return_inverse=True)
    faces = flat.reshape(-1, 3)
    crosses = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    areas = np.linalg.norm(crosses, axis=1) / 2
    assert areas.min() > 1e-8, 'Degenerate triangle'
    assert len(np.unique(np.sort(faces, axis=1), axis=0)) == len(faces), 'Duplicate face'
    edges = np.concatenate((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
    keys = np.sort(edges, axis=1)
    unique_edges, indices, counts = np.unique(keys, axis=0, return_inverse=True, return_counts=True)
    assert np.all(counts == 2), 'Boundary or non-manifold edge'
    directions = np.where(edges[:, 0] < edges[:, 1], 1, -1)
    sums = np.bincount(indices, weights=directions)
    assert np.all(sums == 0), 'Inconsistent face winding'
    graph = nx.Graph()
    graph.add_edges_from(unique_edges)
    bodies = nx.number_connected_components(graph)
    assert bodies == 1, f'Disconnected bodies: {bodies}'
    volume = float(np.einsum('ij,ij->i', tris[:, 0], np.cross(tris[:, 1], tris[:, 2])).sum() / 6)
    assert volume > 0, 'Negative signed volume'
    assert abs(volume - exact_volume) / exact_volume < 0.005, 'Mesh volume disagrees with CAD'
    size = points.max(axis=0) - points.min(axis=0)
    assert np.allclose(size, expected_size, atol=0.001)
    assert abs(points[:, 2].min()) < 0.0001, 'Part not placed on z=0 printing plane'
    return {'watertight_by_edge_incidence': True, 'consistent_winding': True,
            'connected_body_count': bodies, 'triangles': len(tris), 'vertices_after_welding': len(points),
            'welding_tolerance_mm': 0.0001, 'duplicate_faces': 0, 'degenerate_faces': 0,
            'signed_volume_mm3': volume, 'volume_error_percent': 100 * abs(volume - exact_volume) / exact_volume,
            'bbox_mm': size.tolist(), 'minimum_z_mm': float(points[:, 2].min()),
            'self_intersection_audit': 'Not computed for the tessellated mesh; native saved STEP was validated.'}


def check_3mf(path, exact_volume, expected_size):
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.endswith('.model'))
        root = ET.fromstring(z.read(name))
    assert root.attrib['unit'] == 'millimeter'
    ns = {'m': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
    mesh = root.find('.//m:mesh', ns)
    assert mesh is not None
    vertices = np.array([[float(v.attrib[c]) for c in ('x', 'y', 'z')] for v in mesh.find('m:vertices', ns)])
    faces = np.array([[int(t.attrib[c]) for c in ('v1', 'v2', 'v3')] for t in mesh.find('m:triangles', ns)])
    result = check_triangles(vertices[faces], exact_volume, expected_size)
    result['unit'] = root.attrib['unit']
    result['build_item_count'] = len(root.find('m:build', ns))
    assert result['build_item_count'] == 1
    return result


if __name__ == '__main__':
    cad = json.loads((ROOT / 'checks/cad_validation.json').read_text())
    report = {}
    for part, dims in [('base', [144, 96, 22]), ('lid', [144, 96, 2.5])]:
        name = f'TJC4827_{part}'
        report[part] = {'stl': check_triangles(read_stl(ROOT / 'STL' / (name + '.stl')), cad[part]['volume_mm3'], dims),
                        '3mf': check_3mf(ROOT / '3MF' / (name + '.3mf'), cad[part]['volume_mm3'], dims)}
    (ROOT / 'checks/mesh_validation.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
