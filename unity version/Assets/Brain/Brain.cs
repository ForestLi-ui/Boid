using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Brain : MonoBehaviour
{
    // Start is called before the first frame update
    public int n;
    public int maxX;
    public int maxY;
    public int maxZ;
    public float origin_x;
    public float origin_y;
    public float origin_z;
    void Start()
    {
        origin_x = transform.position[0];
        origin_y = transform.position[1];
        origin_z = transform.position[2];

        GameObject prefab = Resources.Load("Cone") as GameObject;
        for(int i=0; i<n; i++)
        {
            GameObject boid = Instantiate(prefab);
            boid.transform.position = new Vector3(Random.Range(origin_x - maxX, origin_x + maxX), Random.Range(origin_y - maxY, origin_y + maxY), Random.Range(origin_z - maxZ, origin_z + maxZ));
        }
    }

    // Update is called once per frame
    void Update()
    {
        
    }
}
