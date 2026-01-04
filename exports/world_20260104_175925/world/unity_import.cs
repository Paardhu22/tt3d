using UnityEngine;
using UnityEditor;
public class TsuanaWorldImporter : MonoBehaviour
{
    [MenuItem("Tsuana/Import World")]
    static void ImportWorld()
    {
        var path = "world.obj";
        var obj = AssetDatabase.LoadAssetAtPath<GameObject>(path);
        if (obj == null) {
            Debug.LogError("World OBJ not found at " + path);
            return;
        }
        var instance = Instantiate(obj);
        instance.transform.position = Vector3.zero;
        Selection.activeGameObject = instance;
    }
}
