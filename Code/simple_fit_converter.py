"""
Simple FIT File Converter - Uses garminconnect to upload directly
Bypasses fit-tool library issues
"""

from garminconnect import Garmin
import json
from datetime import datetime


class SimpleFitConverter:
    def __init__(self, peloton_auth, garmin_client):
        self.peloton_auth = peloton_auth
        self.garmin_client = garmin_client
    
    def sync_workout(self, workout_data):
        """
        Sync workout directly to Garmin using TCX format
        This bypasses FIT file creation entirely
        """
        import tempfile
        import os
        
        workout_id = workout_data.get('id')
        created_at = workout_data.get('created_at')
        
        # Get workout details
        ride = workout_data.get('ride', {})
        title = ride.get('title', 'Peloton Workout')
        duration = ride.get('duration', 0)
        
        # Get performance data if available
        try:
            perf_data = self.peloton_auth.get_workout_details(workout_id)
            metrics = perf_data.get('metrics', [])
            
            # Get summaries from performance data
            summaries = perf_data.get('summaries', [])
            
            # Extract key metrics from summaries
            distance = 0
            calories = 0
            avg_hr = None
            max_hr = None
            avg_output = None
            max_output = None
            avg_cadence = None
            avg_speed = None
            
            for summary in summaries:
                slug = summary.get('slug', '')
                value = summary.get('value', 0)
                display_unit = summary.get('display_unit', '')
                
                if slug == 'distance':
                    # Convert to meters based on unit
                    if display_unit == 'mi':
                        distance = value * 1609.34  # miles to meters
                    elif display_unit == 'km':
                        distance = value * 1000  # km to meters
                    else:
                        distance = value  # assume already meters
                elif slug == 'calories':
                    calories = value
                elif slug == 'avg_heart_rate':
                    avg_hr = value
                elif slug == 'max_heart_rate':
                    max_hr = value
                elif slug == 'avg_output':
                    avg_output = value
                elif slug == 'max_output':
                    max_output = value
                elif slug == 'avg_cadence':
                    avg_cadence = value
                elif slug == 'avg_speed':
                    avg_speed = value
            
            # If HR not in summaries, get from heart_rate metric
            if not avg_hr or not max_hr:
                for metric in perf_data.get('metrics', []):
                    if metric.get('slug') == 'heart_rate':
                        if not avg_hr:
                            avg_hr = metric.get('average_value')
                        if not max_hr:
                            max_hr = metric.get('max_value')
                        break
            
        except Exception as e:
            perf_data = None
            distance = workout_data.get('total_work', 0) / 1000.0 * 1000  # Fallback
            calories = 0
            avg_hr = None
            max_hr = None
        
        # Create TCX (Training Center XML) - much simpler than FIT
        tcx = self._create_tcx(workout_data, perf_data, distance, calories, avg_hr, max_hr)
        
        # Save TCX to temp file
        temp_dir = tempfile.gettempdir()
        tcx_path = os.path.join(temp_dir, f'peloton_{workout_id}.tcx')
        
        with open(tcx_path, 'w') as f:
            f.write(tcx)
        
        # Upload to Garmin
        try:
            result = self.garmin_client.upload_activity(tcx_path)
            
            # Try to set activity name
            if result:
                try:
                    # Extract activity ID from response
                    activity_id = None
                    if hasattr(result, 'json'):
                        response_data = result.json()
                        activity_id = response_data.get('detailedImportResult', {}).get('activityId')
                    
                    if activity_id:
                        # Create nice activity name
                        from datetime import datetime
                        date_str = datetime.fromtimestamp(created_at).strftime('%Y-%m-%d %H:%M')
                        activity_name = f"{title} - {date_str}"
                        
                        self.garmin_client.set_activity_name(activity_id, activity_name)
                except Exception as name_error:
                    # Activity uploaded but couldn't set name - that's okay
                    pass
            
            # Clean up temp file
            try:
                os.remove(tcx_path)
            except:
                pass
            return {'success': True, 'result': result}
        except Exception as e:
            # Clean up temp file
            try:
                os.remove(tcx_path)
            except:
                pass
            return {'success': False, 'error': str(e)}
    
    def _create_tcx(self, workout_data, perf_data, distance, calories, avg_hr, max_hr):
        """Create a TCX XML file for Garmin with all metrics"""
        from datetime import datetime, timedelta
        
        workout_id = workout_data.get('id')
        created_at = workout_data.get('created_at')
        start_time = datetime.utcfromtimestamp(created_at)
        
        ride = workout_data.get('ride', {})
        duration = ride.get('duration', 0)
        
        # Format timestamp for TCX
        time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        tcx = f'''<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" 
                        xmlns:ns2="http://www.garmin.com/xmlschemas/ActivityExtension/v2"
                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd">
  <Activities>
    <Activity Sport="Biking">
      <Id>{time_str}</Id>
      <Lap StartTime="{time_str}">
        <TotalTimeSeconds>{duration}</TotalTimeSeconds>
        <DistanceMeters>{distance:.2f}</DistanceMeters>
        <Calories>{int(calories)}</Calories>'''
        
        if avg_hr:
            tcx += f'''
        <AverageHeartRateBpm>
          <Value>{int(avg_hr)}</Value>
        </AverageHeartRateBpm>'''
        
        if max_hr:
            tcx += f'''
        <MaximumHeartRateBpm>
          <Value>{int(max_hr)}</Value>
        </MaximumHeartRateBpm>'''
        
        tcx += '''
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
'''
        
        # Add track points with all metrics
        if perf_data and perf_data.get('metrics'):
            tcx += '        <Track>\n'
            
            # Get metrics by slug for easy access
            metrics_by_slug = {}
            for metric in perf_data['metrics']:
                slug = metric.get('slug', '')
                values = metric.get('values', [])
                metrics_by_slug[slug] = values
            
            # Get the length - all arrays should be same length
            num_samples = len(metrics_by_slug.get('output', []))
            
            cumulative_distance = 0.0  # Track distance in meters
            
            # Sample every 5 seconds to keep file reasonable
            for i in range(0, num_samples, 5):
                seconds = i  # Each value is 1 second apart
                point_time = start_time + timedelta(seconds=seconds)
                point_time_str = point_time.strftime('%Y-%m-%dT%H:%M:%SZ')
                
                # Calculate distance from speed if available
                if 'speed' in metrics_by_slug and i < len(metrics_by_slug['speed']):
                    speed_mph = float(metrics_by_slug['speed'][i]) if metrics_by_slug['speed'][i] else 0
                    # Convert mph to km for distance calculation
                    speed_kmh = speed_mph * 1.60934
                    distance_increment = (speed_kmh * 5) / 3600  # km for 5 seconds
                    cumulative_distance += distance_increment * 1000  # convert to meters
                
                tcx += f'          <Trackpoint>\n'
                tcx += f'            <Time>{point_time_str}</Time>\n'
                
                # Add distance to trackpoint
                if cumulative_distance > 0:
                    tcx += f'            <DistanceMeters>{cumulative_distance:.2f}</DistanceMeters>\n'
                
                # Heart rate
                if 'heart_rate' in metrics_by_slug and i < len(metrics_by_slug['heart_rate']):
                    hr = metrics_by_slug['heart_rate'][i]
                    if hr:
                        tcx += f'''            <HeartRateBpm>
              <Value>{int(hr)}</Value>
            </HeartRateBpm>
'''
                
                # Cadence
                if 'cadence' in metrics_by_slug and i < len(metrics_by_slug['cadence']):
                    cadence = metrics_by_slug['cadence'][i]
                    if cadence:
                        tcx += f'            <Cadence>{int(cadence)}</Cadence>\n'
                
                # Extensions for power only (remove speed - Garmin miscalculates it)
                has_extensions = False
                extensions_content = ''
                
                # Power (output)
                if 'output' in metrics_by_slug and i < len(metrics_by_slug['output']):
                    power = metrics_by_slug['output'][i]
                    if power:
                        extensions_content += f'                <ns2:Watts>{int(power)}</ns2:Watts>\n'
                        has_extensions = True
                
                if has_extensions:
                    tcx += f'''            <Extensions>
              <ns2:TPX>
{extensions_content}              </ns2:TPX>
            </Extensions>
'''
                
                tcx += f'          </Trackpoint>\n'
            
            tcx += '        </Track>\n'
        
        tcx += '''      </Lap>
    </Activity>
  </Activities>
</TrainingCenterDatabase>'''
        
        return tcx
