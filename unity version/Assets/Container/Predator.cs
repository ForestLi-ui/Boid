using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.IO;

public class Predator : MonoBehaviour
{
    public Vector3 acceleration;
    public Vector3 velocity;
    public float MAX_SPEED;
    public float MAX_ACC;
    public float VIEW_PORTION;
    public float OBSTACLE_VIEW_PORTION;
    public float VIEW_DISTANCE;
    public float chasing_scale;
    public float obstacle_avoidance_scale;
    public int num_points;
    public int obstacle_num_points;
    private Vector3[] points;
    private Vector3[] obstacle_detection_points;
    private HashSet<GameObject> viewed;
    private List<Vector3> obstacles_diff;
    private float timer = 0.0f;
    public int n;

    private string path;
    private StreamWriter writer;
    [UnityEditor.MenuItem("Tools/Write file")]

    // Start is called before the first frame update
    void Start()
    {
        acceleration = new Vector3(Random.Range(-1 * MAX_ACC, MAX_ACC), Random.Range(-1 * MAX_ACC, MAX_ACC), Random.Range(-1 * MAX_ACC, MAX_ACC));
        velocity = new Vector3(Random.Range(-1 * MAX_SPEED, MAX_SPEED), Random.Range(-1 * MAX_SPEED, MAX_SPEED), Random.Range(-1 * MAX_SPEED, MAX_SPEED));

        points = new Vector3[num_points];
        obstacle_detection_points = new Vector3[obstacle_num_points];
        float phi = (float)(Mathf.PI * (3.0 - Mathf.Sqrt(5)));
        for (int i = 0; i < num_points / VIEW_PORTION; i++)
        {
            float y = 1 - (i / (float)(num_points - 1)) * 2;
            float ry = Mathf.Sqrt(1 - y * y);
            float theta = phi * i;
            float x = Mathf.Cos(theta) * ry;
            float z = Mathf.Sin(theta) * ry;
            points[i] = new Vector3(x, y, z) * VIEW_DISTANCE;
        }
        for (int i = 0; i < obstacle_num_points / OBSTACLE_VIEW_PORTION; i++)
        {
            float y = 1 - (i / (float)(obstacle_num_points - 1)) * 2;
            float ry = Mathf.Sqrt(1 - y * y);
            float theta = phi * i;
            float x = Mathf.Cos(theta) * ry;
            float z = Mathf.Sin(theta) * ry;
            obstacle_detection_points[i] = new Vector3(x, y, z) * VIEW_DISTANCE;
        }
        viewed = new HashSet<GameObject>();
        obstacles_diff = new List<Vector3>();


        // initialize text file
        path = "Assets/Resources/test.txt";
        writer = new StreamWriter(path, true);
    }

    // Update is called once per frame
    void Update()
    {
        // add time
        timer += Time.deltaTime;

        // clamping velocities and acceleration
        clamp();

        // gaining entities in view
        in_view();

        // chasing boids
        chase();

        // obstacle avoidance
        obstacle_avoidance();

        
    }

    void OnCollisionEnter(Collision collision)
    {
        //Check for a match with the specified name on any GameObject that collides with your GameObject
        if (collision.gameObject.name == "Cone(Clone)")
        {
            n--;
            writer.WriteLine(n + " " + timer);
            Debug.Log("hit");
            Destroy(collision.gameObject);
        }
    }
    
    void OnApplicationQuit()
    {
        writer.Close();
    }

    void clamp()
    {
        acceleration = Vector3.ClampMagnitude(acceleration, MAX_ACC);
        velocity += acceleration * Time.deltaTime;
        velocity = Vector3.ClampMagnitude(velocity, MAX_SPEED);
        transform.position += velocity * Time.deltaTime;
        transform.rotation = Quaternion.LookRotation(velocity) * Quaternion.Euler(90, 0, 0);
    }

    void in_view()
    {
        RaycastHit hit;
        viewed = new HashSet<GameObject>();
        obstacles_diff = new List<Vector3>();
        for (int i = 0; i < num_points / VIEW_PORTION; i++)
        {
            // boid detection
            if (Physics.Raycast(transform.position, transform.TransformDirection(points[i]), out hit, VIEW_DISTANCE, 1 << 3))
            {
                viewed.Add(hit.collider.gameObject);
            }
        }
        for (int i = 0; i < obstacle_num_points / OBSTACLE_VIEW_PORTION; i++)
        {
            // obstacle detection
            if (Physics.Raycast(transform.position, transform.TransformDirection(obstacle_detection_points[i]), out hit, VIEW_DISTANCE, 1 << 6))
            {
                Vector3 a = hit.point - transform.position;
                Debug.DrawLine(transform.position, hit.point, Color.red);
                obstacles_diff.Add(a);
            }
        }
    }

    void chase()
    {
        if (viewed.Count > 0)
        {
            Vector3 total = new Vector3(0, 0, 0);
            foreach (GameObject boid in viewed)
            {
                total += boid.transform.position;
            }
            total /= viewed.Count;
            acceleration += (total - transform.position - velocity) * chasing_scale;
        }
    }

    void obstacle_avoidance()
    {
        if (obstacles_diff.Count > 0)
        {
            Vector3 average = new Vector3(0, 0, 0);
            foreach (Vector3 diff in obstacles_diff)
            {
                float distance = hypot(diff) + 0.0000000001f;
                average += diff / Mathf.Pow(distance, 2);
            }
            acceleration -= (average / obstacles_diff.Count) * obstacle_avoidance_scale;
        }
    }

    float hypot(Vector3 diff)
    {
        return Mathf.Sqrt(Mathf.Pow(diff[0], 2) + Mathf.Pow(diff[1], 2) + Mathf.Pow(diff[2], 2));
    }
}
